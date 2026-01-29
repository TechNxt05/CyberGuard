import sys
from typing import Optional
import os
import logging
from contextlib import asynccontextmanager

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Add project root to sys.path to allow 'backend' imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.app.schemas.common import AnalysisRequest, ScamAnalysisResult
from backend.app.schemas.resolution import IncidentRequest, CaseState
from backend.app.schemas.interactive import DoubtRequest, DoubtResponse, FormAssistRequest, FormAssistResponse
from backend.app.workflows.scamshield_graph import scamshield_app
from backend.app.workflows.cyber_resolve_graph import cyber_resolve_app
from backend.app.agents.resolution.state_agent import get_case_state as get_agent_case_state
from backend.app.agents.resolution.assistants import resolve_doubt, assist_form
from backend.app.auth.clerk_auth import get_current_user
from backend.app.db.mongodb import db
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB
    await db.connect()
    yield
    # Shutdown: Close connection
    await db.close()

app = FastAPI(title="CyberGuardAI One - Platform Backend", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "CyberGuardAI Platform Online", "auth": "Clerk Enabled", "db": "MongoDB Atlas"}

# ==========================================
# PUBLIC ROUTES (ScamShield - No Login Required)
# ==========================================

@app.post("/analyze-message", response_model=ScamAnalysisResult)
async def analyze_message(request: AnalysisRequest):
    """
    Main endpoint for analyzing suspicious messages.
    Triggers the Multi-Agent LangGraph workflow.
    """
    try:
        initial_state = {"request": request, "user_profile": None, "scout_report": None, "explanation": None, "action_plan": None, "final_output": None}
        result = await scamshield_app.ainvoke(initial_state)
        if "final_output" in result:
             return result["final_output"]
        raise HTTPException(status_code=500, detail="Analysis produced no output")
    except Exception as e:
        print(f"Error in analyze-message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# AUTHENTICATED CASE MANAGEMENT (New)
# ==========================================

@app.get("/cases")
async def list_cases(user_id: str = Depends(get_current_user)):
    """List all cases for the logged-in user."""
    from backend.app.mcp_servers.memory.server import list_user_cases
    return await list_user_cases(user_id)

@app.post("/cases")
async def create_new_case(title: str, summary: str, user_id: str = Depends(get_current_user)):
    """Create a new case."""
    from backend.app.mcp_servers.memory.server import create_case
    return {"case_id": await create_case(user_id, title, summary)}

@app.get("/cases/{case_id}")
async def get_case_details(case_id: str, user_id: str = Depends(get_current_user)):
    """Get full details of a specific case."""
    from backend.app.mcp_servers.memory.server import get_case, get_case_history, get_tasks
    case = await get_case(user_id, case_id)
    if "error" in case:
        raise HTTPException(status_code=404, detail="Case not found")
    history = await get_case_history(case_id, user_id)
    tasks = await get_tasks(case_id, user_id)
    
    # Sanitize case for JSON serialization
    if case and "_id" in case:
        case["_id"] = str(case["_id"])
        
    return {"case": case, "history": history, "tasks": tasks}

class ChatRequest(BaseModel):
    message: str
    image_base64: Optional[str] = None

@app.post("/cases/{case_id}/chat")
async def chat_with_case(case_id: str, chat_req: ChatRequest, user_id: str = Depends(get_current_user)):
    """Send a message to the AI agent for a specific case."""
    from backend.app.mcp_servers.memory.server import add_case_message, get_case_state
    
    # 1. Save User Message
    msg_content = chat_req.message
    if chat_req.image_base64:
        msg_content += "\n[Image Uploaded]"
    
    await add_case_message(case_id, user_id, "user", msg_content)
    
    # 2. Get Context (State + History)
    state_data = await get_case_state(case_id, user_id)
    
    # 3. Vision Analysis (Early Exit or Context Injection)
    vision_context = ""
    if chat_req.image_base64:
        # Perform Vision Analysis
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        from langchain_core.messages import HumanMessage
        
        if os.getenv("GEMINI_API_KEY"):
            try:
                vision_llm = ChatGoogleGenerativeAI(
                    google_api_key=os.getenv("GEMINI_API_KEY"),
                    model="gemini-1.5-flash",
                    temperature=0.1
                )
                ocr_message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Analyze this image relevant to a cybercrime case. Extract full text, identify any suspicious elements (URLs, phone numbers, transaction IDs), and describe the visual context."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{chat_req.image_base64}"}},
                    ]
                )
                msg_response = await vision_llm.ainvoke([ocr_message])
                vision_context = f"\n\n[SYSTEM: Image Analysis Result]:\n{msg_response.content}"
                
                # Append analysis to chat for context
                # We won't save this analysis as a separate message to avoid clutter, 
                # but we will use it in the prompt.
            except Exception as e:
                print(f"Vision Error: {e}")
                vision_context = "\n\n[SYSTEM]: Image upload failed analysis."
    
    # 4. Check if we need to run the Initial Resolution Plan
    ai_response = ""
    
    if not state_data or "strategy" not in state_data:
        try:
            # Create Initial Request from User Message + Vision Context
            full_description = chat_req.message + vision_context
            req = IncidentRequest(description=full_description, user_context={"user_id": user_id})
            
            # Invoke Graph
            initial_state = {"request": req, "case_state": None, "current_guide": None}
            result = await cyber_resolve_app.ainvoke(initial_state)
            
            # Extract Results
            new_case_state = result["case_state"]
            ai_response = result["current_guide"] or "I have analyzed your incident. Please check the tasks in the sidebar."
            
            # Save State to DB
            from backend.app.mcp_servers.memory.server import update_case_state, add_task
            await update_case_state(case_id, user_id, new_case_state.model_dump())
            
            # Sync Tasks to DB (for Sidebar)
            if new_case_state.strategy and new_case_state.strategy.lifecycle_plan:
                from backend.app.mcp_servers.authority_source.server import get_official_link
                
                for step in new_case_state.strategy.lifecycle_plan:
                    # HEURISTIC: Enrich Task with Link if mention found
                    # Ideally this logic belongs in the 'Guide' agent, but for MVP speed we do it here.
                    link = None
                    atype = None
                    
                    if "1930" in step.action:
                        link = "tel:1930"
                        atype = "call"
                    elif "cybercrime.gov" in step.action or "portal" in step.action:
                         # Fetch verified link
                         data = get_official_link("cybercrime.gov.in")
                         if "file_complaint" in data:
                             link = data["file_complaint"]
                             atype = "link"
                    
                    await add_task(
                        case_id, 
                        user_id, 
                        label=step.action, 
                        description=step.description,
                        action_link=link,
                        action_type=atype
                    )
            
        except Exception as e:
            print(f"Graph Error: {e}")
            ai_response = "I encountered an error analyzing your request. Please try again with more details."
    else:
        # Existing Case Handling (Follow-up)
        # Using a simple LLM call here for now, injected with history and vision context
        from backend.app.services.llm_provider import get_llm
        from langchain_core.messages import SystemMessage, HumanMessage
        
        # Determine Form Assistance
        if "draft" in chat_req.message.lower() or "write" in chat_req.message.lower():
             ai_response = await generate_form_text(state_data.get("dimensions", {}))
        else:
            # General Chat with Context
            llm = get_llm()
            
            # Construct History Context (Last 5 messages)
            from backend.app.mcp_servers.memory.server import get_case_history
            history = await get_case_history(case_id, user_id)
            history_text = "\n".join([f"{m['sender'].upper()}: {m['content']}" for m in history[-5:]])
            
            prompt = f"""
            You are CyberGuard, an expert cybersecurity assistant helping a user with Case ID {case_id}.
            
            Current Case Status: {state_data.get('status', 'Unknown')}
            Strategy Overview: {state_data.get('strategy', {}).get('estimated_timeline', 'N/A')}
            
            Recent Chat History:
            {history_text}
            
            User's Latest Input: "{chat_req.message}"
            
            {vision_context}
            
            Provide a helpful, direct response. If the user uploaded an image, reference the analysis provided above.
            """
            
            resp = await llm.ainvoke([HumanMessage(content=prompt)])
            ai_response = resp.content

    # 4. Save AI Response
    await add_case_message(case_id, user_id, "agent", ai_response)
    
    return {"reply": ai_response}

@app.post("/cases/{case_id}/chat")
async def chat_with_case(case_id: str, chat_req: ChatRequest, user_id: str = Depends(get_current_user)):
    """Send a message to the AI agent for a specific case."""
    logger.info(f"--- DEBUG: chat_with_case HANDLER STARTED for case {case_id} ---")
    from backend.app.mcp_servers.memory.server import add_case_message, get_case_state
    
    # 1. Save User Message
    await add_case_message(case_id, user_id, "user", chat_req.message)
    
    # 2. Get Context (State + History)
    state_data = await get_case_state(case_id, user_id)
    
    # 3. Check if we need to run the Initial Resolution Plan
    # If the case has no strategy/dimensions, it's a "fresh" cae needing analysis.
    ai_response = ""
    
    if not state_data or "strategy" not in state_data:
        try:
            # Create Initial Request from User Message
            req = IncidentRequest(description=chat_req.message, user_context={"user_id": user_id})
            
            # Invoke Graph
            initial_state = {"request": req, "case_state": None, "current_guide": None}
            result = await cyber_resolve_app.ainvoke(initial_state)
            
            # Extract Results
            logger.info("--- DEBUG: Graph finished. Extracting results. ---")
            new_case_state = result["case_state"]
            ai_response = result["current_guide"] or "I have analyzed your incident. Please check the tasks in the sidebar."
            
            # Save State to DB
            print("--- DEBUG: Importing memory tools. ---", flush=True)
            try:
                from backend.app.mcp_servers.memory.server import update_case_state, add_task, update_case_details
            except ImportError as ie:
                print(f"!!! CRITICAL ERROR importing memory tools: {ie} !!!", flush=True)
                raise ie
            
            print("--- DEBUG: Saving Case State. ---", flush=True)
            await update_case_state(case_id, user_id, new_case_state.model_dump())
            print("--- DEBUG: Case State Saved. ---", flush=True)
            
            # Sync Case Details (Summary, Attack Type, etc.)
            try:
                print(f"--- DEBUG: Attempting to update case details for {case_id} ---", flush=True)
                details_payload = {
                    "incident_summary": new_case_state.dimensions.summary,
                    "attack_type": new_case_state.dimensions.attack_type,
                    "incident_logic": new_case_state.dimensions.incident_logic,
                    "prevention_tips": new_case_state.dimensions.prevention_tips
                }
                print(f"--- DEBUG: Payload Keys: {list(details_payload.keys())} ---", flush=True)
                print(f"--- DEBUG: Payload Summary: {details_payload['incident_summary'][:50]}... ---", flush=True)
                
                await update_case_details(case_id, user_id, details_payload)
                print("--- DEBUG: update_case_details completed successfully ---", flush=True)
            except Exception as e:
                print(f"!!! CRITICAL ERROR updating case details: {e} !!!", flush=True)
                import traceback
                print(traceback.format_exc(), flush=True)
            
            # Sync Tasks to DB (for Sidebar)
            if new_case_state.strategy and new_case_state.strategy.lifecycle_plan:
                print(f"--- DEBUG: Syncing {len(new_case_state.strategy.lifecycle_plan)} tasks. ---", flush=True)
                for step in new_case_state.strategy.lifecycle_plan:
                    await add_task(case_id, user_id, label=step.action, description=step.description)
            else:
                print("--- DEBUG: No strategy/tasks to sync. ---", flush=True)
            
        except Exception as e:
            print(f"Graph Error: {e}", flush=True)
            ai_response = "I encountered an error analyzing your request. Please try again with more details."
    else:
        # TODO: Implement Follow-up / Doubt Resolution logic here for existing cases
        # For now, acknowledge context
        ai_response = "I have your plan ready. Please check the tasks sidebar. How can I assist you with the current step?"

    # 4. Save AI Response
    await add_case_message(case_id, user_id, "agent", ai_response)
    
    # 5. Get Updated Tasks (to refresh Sidebar)
    # Add small delay to ensure DB writes are propagated
    import asyncio
    await asyncio.sleep(1.0)
    
    from backend.app.mcp_servers.memory.server import get_tasks, get_case
    current_tasks = await get_tasks(case_id, user_id)
    updated_case = await get_case(user_id, case_id)
    
    # Sanitize updated_case for JSON serialization (handle ObjectId)
    if updated_case and "_id" in updated_case:
        updated_case["_id"] = str(updated_case["_id"])
    
    response_payload = {
        "reply": ai_response, 
        "tasks": current_tasks, 
        "case_details": updated_case
    }
    
    logger.info(f"--- DEBUG: Final Response Keys: {list(response_payload.keys())} ---")
    if updated_case:
        logger.info(f"--- DEBUG: Case Details Summary: {updated_case.get('incident_summary')} ---")
    
    return response_payload

# ==========================================
# LEGACY / SPECIFIC RESOLUTION ROUTES
# (To be refactored into Case Chat)
# ==========================================

@app.post("/resolve-incident", response_model=CaseState)
async def resolve_incident_endpoint(request: IncidentRequest):
    """
    Legacy endpoint - will eventually move to /cases flow.
    """
    try:
        initial_state = {"request": request, "case_state": None, "current_guide": None}
        result = await cyber_resolve_app.ainvoke(initial_state)
        return result["case_state"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/cases/{case_id}/tasks/{label}")
async def update_task(case_id: str, label: str, status: str, user_id: str = Depends(get_current_user)):
    """Manually updates a task status."""
    from backend.app.mcp_servers.memory.server import update_task_status
    await update_task_status(case_id, user_id, label, status)
    return {"status": "success"}
def solve_doubt_endpoint(req: DoubtRequest):
    try:
        case = get_agent_case_state(req.incident_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        plan_summary = f"Attack: {case.dimensions.attack_type}. Current Status: {case.status}."
        answer = resolve_doubt(req.question, plan_summary)
        return DoubtResponse(answer=answer)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/case/form-assist", response_model=FormAssistResponse)
def form_assistance_endpoint(req: FormAssistRequest):
    try:
        case = get_agent_case_state(req.incident_id)
        if not case:
            raise HTTPException(status_code=404, detail="Case not found")
        guidance = assist_form(req.action_item)
        return FormAssistResponse(guidance=guidance, checklist=[]) 
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "up", "db_connected": db.client is not None}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
