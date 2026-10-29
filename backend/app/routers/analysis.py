import base64
import json
import logging
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth.clerk_auth import get_current_user
from app.schemas.confidence import ConfidenceRequest, ConfidenceResponse
from app.schemas.graph import GraphRequest, GraphResponse
from app.schemas.timeline import TimelineRequest, TimelineResponse
from app.services.llm_provider import LLMUnavailableError, astructured_call
from app.services.rate_limit import llm_light

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

MAX_IMAGE_BYTES = 5 * 1024 * 1024
MAX_AUDIO_BYTES = 20 * 1024 * 1024  # Groq's free Whisper endpoint accepts up to 25 MB


async def _read_upload(file: UploadFile, max_bytes: int, allowed_prefix: str) -> bytes:
    if not (file.content_type or "").startswith(allowed_prefix):
        raise HTTPException(status_code=415, detail=f"Expected a {allowed_prefix.rstrip('/')} file.")
    contents = await file.read(max_bytes + 1)
    if len(contents) > max_bytes:
        raise HTTPException(status_code=413, detail=f"File too large (max {max_bytes // (1024 * 1024)} MB).")
    return contents


def _unavailable(what: str, error: Exception) -> HTTPException:
    logger.error("%s failed: %s", what, error)
    if isinstance(error, LLMUnavailableError):
        return HTTPException(status_code=503, detail=str(error))
    return HTTPException(status_code=503, detail=f"{what} is temporarily unavailable. Please try again.")


@router.post("/analyze-image", dependencies=[Depends(llm_light)])
async def analyze_image(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    """Analyzes an uploaded screenshot for cyber threats."""
    from app.services.vision_engine import VisionEngine

    contents = await _read_upload(file, MAX_IMAGE_BYTES, "image/")
    try:
        result = await VisionEngine().analyze_screenshot(base64.b64encode(contents).decode("utf-8"), file.content_type)
    except Exception as e:
        raise _unavailable("Image analysis", e)
    return {"status": "success", "analysis": result}


@router.post("/analyze-audio", dependencies=[Depends(llm_light)])
async def analyze_audio(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    """Transcribes a call recording (Groq Whisper) and assesses it for scam patterns."""
    from app.services.audio_engine import AudioEngine

    contents = await _read_upload(file, MAX_AUDIO_BYTES, "audio/")
    try:
        result = await AudioEngine().analyze_audio(contents, file.filename or "recording")
    except Exception as e:
        raise _unavailable("Audio analysis", e)
    return {"status": "success", "analysis": result}


@router.post("/confidence", response_model=ConfidenceResponse, dependencies=[Depends(llm_light)])
async def analyze_confidence(req: ConfidenceRequest, user_id: str = Depends(get_current_user)):
    """Threat likelihood, urgency and priority actions for an incident."""
    system = (
        "You are a Cyber Threat Intelligence expert. Assess the incident. Scores are integers 0-100; "
        "attackSophistication and urgencyLevel are one of LOW, MEDIUM, HIGH, CRITICAL; "
        "each priority action's impact is one of LOW, MEDIUM, HIGH, CRITICAL. Base every score on the description only."
    )
    user = f"Incident description: {req.incidentDescription}\nExtracted entities: {json.dumps(req.extractedEntities)}"
    try:
        return await astructured_call(system, user, ConfidenceResponse, temperature=0.2)
    except Exception as e:
        raise _unavailable("Threat assessment", e)


@router.post("/timeline", response_model=TimelineResponse, dependencies=[Depends(llm_light)])
async def analyze_timeline(req: TimelineRequest, user_id: str = Depends(get_current_user)):
    """Reconstructs the attack timeline from the description."""
    system = (
        "You are a cyber forensics expert. Reconstruct a chronological timeline of the attack using ONLY events stated "
        "or clearly implied in the description. eventType is one of reconnaissance, initial_access, execution, "
        "exfiltration, impact. Use ISO 8601 timestamps when the description gives times; otherwise use relativeTime "
        "(e.g. T+0, T+5 mins) and leave timestamp as an empty string."
    )
    try:
        result = await astructured_call(system, f"Incident description: {req.incidentDescription}", TimelineResponse, temperature=0.1)
    except Exception as e:
        raise _unavailable("Timeline reconstruction", e)
    for ev in result.events:
        ev.id = ev.id or str(uuid.uuid4())
    return result


@router.post("/graph", response_model=GraphResponse, dependencies=[Depends(llm_light)])
async def analyze_graph(req: GraphRequest, user_id: str = Depends(get_current_user)):
    """Builds an entity relationship graph for the incident."""
    system = (
        "You are a cyber threat intelligence analyst. Extract a relationship graph of the entities in this incident. "
        "Node type is one of victim, threat_actor, mule_account, url, ip, wallet, email, phone. Node ids must be unique "
        "and every edge must reference existing node ids. Only include entities that appear in the input."
    )
    user = f"Incident description: {req.incidentDescription}\nExtracted entities: {json.dumps(req.extractedEntities)}"
    try:
        return await astructured_call(system, user, GraphResponse, temperature=0.1)
    except Exception as e:
        raise _unavailable("Graph extraction", e)
