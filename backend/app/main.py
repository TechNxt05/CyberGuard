import base64
import binascii
import hashlib
import json
import logging
import os
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Literal, Optional

from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

if os.getenv("SENTRY_DSN"):
    import sentry_sdk

    # Free-tier friendly: errors only, no performance tracing; never send request bodies (victim data).
    sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), send_default_pii=False, traces_sample_rate=0.0,
                    environment=os.getenv("SENTRY_ENVIRONMENT", "production"))

import time  # noqa: E402
import uuid  # noqa: E402

from fastapi import Depends, FastAPI, HTTPException, Request  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.encoders import jsonable_encoder  # noqa: E402
from fastapi.responses import JSONResponse, StreamingResponse  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from app.agents.resolution.assistants import assist_form, resolve_doubt  # noqa: E402
from app.agents.resolution.form_assistant import generate_form_text  # noqa: E402
from app.auth.clerk_auth import get_current_user  # noqa: E402
from app.db.mongodb import db  # noqa: E402
from app.routers import analysis, community, investigate, memory, reports, telegram_bot, threat_feed, url_check  # noqa: E402
from app.schemas.case import Task  # noqa: E402
from app.schemas.common import MAX_IMAGE_BASE64_CHARS, MAX_TEXT_CHARS, AnalysisRequest, ScamAnalysisResult  # noqa: E402
from app.schemas.interactive import DoubtRequest, DoubtResponse, FormAssistRequest, FormAssistResponse  # noqa: E402
from app.schemas.resolution import IncidentRequest  # noqa: E402
from app.services import case_store  # noqa: E402
from app.services.authority_directory import get_official_link  # noqa: E402
from app.services.memory_service import ThreatMemoryService  # noqa: E402
from app.services.llm_provider import atext_call, get_vision_llm, image_message, response_text  # noqa: E402
from app.services.rate_limit import llm_heavy, llm_light, read_only  # noqa: E402
from app.workflows.cyber_resolve_graph import cyber_resolve_app, run_resolution  # noqa: E402
from app.workflows.scamshield_graph import scamshield_app  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db.connect()
    if db.db is not None:
        try:
            await ThreatMemoryService(db.db).ensure_indexes()
            await case_store.ensure_indexes()
        except Exception as e:
            logger.error("Could not create MongoDB indexes: %s", e)
    yield
    await db.close()


app = FastAPI(title="CyberGuardAI Platform Backend", version="2.1.0", lifespan=lifespan)

# Comma-separated list, e.g. "https://cyberguard.vercel.app,http://localhost:3000".
ALLOWED_ORIGINS = [o.strip().rstrip("/") for o in os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Optional, e.g. "https://cyberguard-.*\.vercel\.app" to allow Vercel preview deployments.
    allow_origin_regex=os.getenv("ALLOWED_ORIGIN_REGEX") or None,
    allow_credentials=False,  # auth uses bearer tokens, not cookies
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.middleware("http")
async def request_log(request: Request, call_next):
    """One log line per request with a request id, so slow or failing calls are easy to find in Render logs."""
    request_id = request.headers.get("x-request-id") or uuid.uuid4().hex[:12]
    started = time.perf_counter()
    status = 500
    try:
        response = await call_next(request)
        status = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        if request.url.path != "/health":  # keep-alive pings would drown everything else
            logger.info("%s %s %s %.0fms rid=%s", request.method, request.url.path, status, (time.perf_counter() - started) * 1000, request_id)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Log the details, but never leak internals (stack traces, keys, DB errors) to the client.
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


app.include_router(analysis.router)
app.include_router(investigate.router)
app.include_router(memory.router)
app.include_router(reports.router)
app.include_router(threat_feed.router)
app.include_router(telegram_bot.router)
app.include_router(url_check.router)
app.include_router(community.router)


@app.get("/")
def read_root():
    return {"status": "CyberGuardAI Platform Online"}


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat() + "Z", "db_configured": db.client is not None}


# ==========================================
# PUBLIC ROUTES (no login, rate limited)
# ==========================================

@app.post("/analyze-message", response_model=ScamAnalysisResult, dependencies=[Depends(llm_heavy)])
async def analyze_message(request: AnalysisRequest):
    """ScamShield: profile -> detect -> web research -> explain + action plan."""
    if not (request.message or "").strip() and not request.image_base64:
        raise HTTPException(status_code=400, detail="Provide a message or a screenshot.")
    result = await scamshield_app.ainvoke({"request": request})
    return result["final_output"]


@app.post("/resolve-incident", dependencies=[Depends(llm_heavy)])
async def resolve_incident_endpoint(request: IncidentRequest):
    """Anonymous one-off resolution plan (nothing is stored). Signed-in users get persistent cases via /cases."""
    case_state, guide = await run_resolution(request)
    return {"case_state": case_state, "guide": guide}


# ---- Streaming variants: Server-Sent Events so the UI can show each step as it finishes ----

STEP_LABELS = {
    "profiler": "Understanding who the message targets",
    "detector": "Checking the message, links and known scam patterns",
    "research": "Searching the web for reports of this scam",
    "advisor": "Writing your explanation and action plan",
    "memory": "Finalising",
    "understanding": "Classifying the incident",
    "evidence": "Extracting indicators",
    "strategy": "Building your recovery plan",
    "recovery": "Writing step-by-step guidance",
    "authority_mapper": "Finding the right authorities",
    "prevention": "Collecting prevention tips",
}


def _sse(event: str, data) -> str:
    return f"event: {event}\ndata: {json.dumps(jsonable_encoder(data))}\n\n"


async def _stream_graph(graph, initial_state: dict, finish):
    """Runs a LangGraph workflow, emitting a `progress` event per node and a final `result` (or `error`)."""
    state = dict(initial_state)
    try:
        async for update in graph.astream(initial_state, stream_mode="updates"):
            for node, changes in update.items():
                state.update(changes or {})
                yield _sse("progress", {"step": node, "label": STEP_LABELS.get(node, node)})
        yield _sse("result", finish(state))
    except Exception:
        logger.exception("Streaming workflow failed")
        yield _sse("error", {"detail": "The analysis failed. Please try again in a minute."})


def _event_stream(generator) -> StreamingResponse:
    # X-Accel-Buffering stops proxies from buffering the stream into one late chunk.
    return StreamingResponse(generator, media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.post("/analyze-message/stream", dependencies=[Depends(llm_heavy)])
async def analyze_message_stream(request: AnalysisRequest):
    if not (request.message or "").strip() and not request.image_base64:
        raise HTTPException(status_code=400, detail="Provide a message or a screenshot.")
    return _event_stream(_stream_graph(scamshield_app, {"request": request}, lambda s: s["final_output"]))


@app.post("/resolve-incident/stream", dependencies=[Depends(llm_heavy)])
async def resolve_incident_stream(request: IncidentRequest):
    initial = {"request": request, "case_state": None, "current_guide": None}
    return _event_stream(_stream_graph(cyber_resolve_app, initial, lambda s: {"case_state": s["case_state"], "guide": s.get("current_guide")}))


@app.post("/case/doubt", response_model=DoubtResponse, dependencies=[Depends(llm_light)])
async def solve_doubt_endpoint(req: DoubtRequest):
    return DoubtResponse(answer=await resolve_doubt(req.question, req.context, req.language))


@app.post("/case/form-assist", response_model=FormAssistResponse, dependencies=[Depends(llm_light)])
async def form_assistance_endpoint(req: FormAssistRequest):
    return FormAssistResponse(guidance=await assist_form(req.action_item, [req.context] if req.context else None, req.language), checklist=[])


# ==========================================
# AUTHENTICATED CASE MANAGEMENT
# ==========================================

class CreateCaseRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    summary: str = Field("", max_length=2000)


class ChatRequest(BaseModel):
    message: str = Field("", max_length=MAX_TEXT_CHARS)
    image_base64: Optional[str] = Field(None, max_length=MAX_IMAGE_BASE64_CHARS)
    image_mime_type: Optional[str] = Field("image/jpeg", pattern=r"^image/(png|jpeg|jpg|webp|gif)$")


class TaskStatusRequest(BaseModel):
    status: Literal["pending", "in_progress", "completed", "blocked"]


async def _owned_case(case_id: str, user_id: str) -> dict:
    case = await case_store.get_case(user_id, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@app.get("/cases", dependencies=[Depends(read_only)])
async def list_cases(user_id: str = Depends(get_current_user)):
    return await case_store.list_user_cases(user_id)


@app.post("/cases", dependencies=[Depends(read_only)])
async def create_new_case(req: CreateCaseRequest, user_id: str = Depends(get_current_user)):
    return {"case_id": await case_store.create_case(user_id, req.title, req.summary)}


@app.get("/cases/{case_id}", dependencies=[Depends(read_only)])
async def get_case_details(case_id: str, user_id: str = Depends(get_current_user)):
    case = await _owned_case(case_id, user_id)
    return {
        "case": case,
        "history": await case_store.get_case_history(case_id, user_id),
        "tasks": await case_store.get_tasks(case_id, user_id),
    }


@app.delete("/cases/{case_id}", dependencies=[Depends(read_only)])
async def delete_case(case_id: str, user_id: str = Depends(get_current_user)):
    """Permanently deletes a case with its messages, tasks and analysis state."""
    if not await case_store.delete_case(case_id, user_id):
        raise HTTPException(status_code=404, detail="Case not found")
    await ThreatMemoryService(db.db).forget_case(case_id)
    await case_store.audit("case_deleted", user_id)
    return {"status": "deleted"}


@app.get("/me/data", dependencies=[Depends(read_only)])
async def export_my_data(user_id: str = Depends(get_current_user)):
    """Everything stored about the signed-in user (data portability)."""
    return await case_store.export_user_data(user_id)


@app.delete("/me/data", dependencies=[Depends(read_only)])
async def delete_my_data(user_id: str = Depends(get_current_user)):
    """Deletes all of the user's cases and withdraws their reports from threat memory."""
    counts = await case_store.delete_user_data(user_id)
    await ThreatMemoryService(db.db).forget_reporter(user_id)
    await case_store.audit("user_data_deleted", user_id, counts)
    return {"status": "deleted", "deleted": counts}


@app.put("/cases/{case_id}/tasks/{task_id}", dependencies=[Depends(read_only)])
async def update_task(case_id: str, task_id: str, req: TaskStatusRequest, user_id: str = Depends(get_current_user)):
    if not await case_store.update_task_status(case_id, user_id, task_id, req.status):
        raise HTTPException(status_code=404, detail="Task not found")
    return {"status": "success"}


async def _describe_image(image_base64: str, mime_type: str) -> str:
    prompt = (
        "Analyze this image relevant to a cybercrime case. Extract the full text, identify suspicious elements "
        "(URLs, phone numbers, UPI IDs, transaction IDs), and describe the visual context."
    )
    try:
        response = await get_vision_llm().ainvoke([image_message(prompt, image_base64, mime_type)])
        return response_text(response.content)
    except Exception as e:
        logger.warning("Case image analysis failed: %s", e)
        return ""


def _task_link(action: str) -> tuple[Optional[str], Optional[str]]:
    if "1930" in action:
        return "tel:1930", "call"
    if "cybercrime.gov" in action.lower() or "portal" in action.lower():
        data = get_official_link("cybercrime.gov.in")
        return data.get("file_complaint"), "link"
    return None, None


async def _start_case(case_id: str, user_id: str, description: str) -> str:
    """First message on a case: run the full resolution workflow and persist plan, tasks and details."""
    case_state, guide = await run_resolution(IncidentRequest(description=description[:MAX_TEXT_CHARS], user_context={"country": "India"}))
    await case_store.update_case_state(case_id, user_id, case_state.model_dump(mode="json"))

    plan = case_state.strategy.lifecycle_plan
    tasks = []
    for step in plan:
        link, link_type = _task_link(step.action)
        tasks.append(Task(label=step.action, description=step.description, action_link=link, action_type=link_type))
    await case_store.add_tasks(case_id, user_id, tasks)

    dims = case_state.dimensions
    await case_store.update_case_details(case_id, user_id, {
        "incident_summary": dims.summary,
        "attack_type": dims.attack_type,
        "incident_logic": dims.incident_logic,
        "prevention_tips": dims.prevention_tips,
        "current_phase": plan[0].phase if plan else "analysis",
    })
    return guide or "I've analysed your incident and created a step-by-step plan. Check the tasks in the sidebar."


async def _follow_up(case_id: str, user_id: str, state_data: dict, message: str) -> str:
    dimensions = state_data.get("dimensions", {})
    if re.search(r"\b(draft|fir)\b|complaint text|write (the|my|a) complaint", message.lower()):
        return await generate_form_text(dimensions, message)

    history = await case_store.get_case_history(case_id, user_id, limit=8)
    history_text = "\n".join(f"{m['sender'].upper()}: {m['content']}" for m in history)
    plan = state_data.get("strategy", {}).get("lifecycle_plan", [])
    plan_text = "\n".join(f"- [{s.get('phase')}] {s.get('action')}" for s in plan[:10])
    return await atext_call(
        "You are CyberGuard, an expert assistant helping a cybercrime victim through their recovery plan. "
        "Be direct and practical. Never ask for OTPs, passwords or card numbers.",
        f"Incident: {dimensions.get('summary', 'unknown')} (type: {dimensions.get('attack_type', 'unknown')})\n"
        f"Current plan:\n{plan_text or 'none'}\n\nRecent conversation:\n{history_text}\n\nUser's latest message: {message}",
        temperature=0.4,
    )


@app.post("/cases/{case_id}/chat", dependencies=[Depends(llm_heavy)])
async def chat_with_case(case_id: str, chat_req: ChatRequest, user_id: str = Depends(get_current_user)):
    """Send a message (and optional screenshot) to the AI assistant for a specific case."""
    await _owned_case(case_id, user_id)
    if not chat_req.message.strip() and not chat_req.image_base64:
        raise HTTPException(status_code=400, detail="Message is empty.")

    message = chat_req.message
    attachment = None
    if chat_req.image_base64:
        image_text = await _describe_image(chat_req.image_base64, chat_req.image_mime_type or "image/jpeg")
        if image_text:
            message = f"{message}\n\n[Screenshot analysis]\n{image_text}"
        # The screenshot itself is not stored; its SHA-256 lets the user prove later that the file they
        # submit to the police is the one analysed here.
        try:
            raw = base64.b64decode(chat_req.image_base64, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(status_code=400, detail="Invalid image data.")
        attachment = {
            "sha256": hashlib.sha256(raw).hexdigest(),
            "mime_type": chat_req.image_mime_type,
            "size_bytes": len(raw),
            "extracted_text": image_text[:4000],
        }

    await case_store.add_case_message(case_id, user_id, "user", chat_req.message + ("\n[Image uploaded]" if attachment else ""), attachment)

    state_data = await case_store.get_case_state(case_id, user_id)
    try:
        if not state_data.get("strategy"):
            reply = await _start_case(case_id, user_id, message)
        else:
            reply = await _follow_up(case_id, user_id, state_data, message)
    except Exception:
        logger.exception("Case chat failed for case %s", case_id)
        reply = "I couldn't process that right now (the AI service may be busy). Please try again in a minute."

    await case_store.add_case_message(case_id, user_id, "agent", reply)
    return {
        "reply": reply,
        "tasks": await case_store.get_tasks(case_id, user_id),
        "case_details": await case_store.get_case(user_id, case_id),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
