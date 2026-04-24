from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from backend.app.auth.clerk_auth import get_current_user
from backend.app.db.mongodb import db
from backend.app.schemas.case import Evidence, TimelineEvent

router = APIRouter(prefix="/api/evidence", tags=["Evidence"])

class ExtractEvidenceRequest(BaseModel):
    case_id: str
    text_content: str

@router.post("/extract-evidence")
async def extract_evidence(request: ExtractEvidenceRequest, user_id: str = Depends(get_current_user)):
    """Extracts structured entities from text and saves to Evidence locker."""
    from backend.app.services.vision_engine import FraudEntityExtractor
    
    extractor = FraudEntityExtractor()
    entities = await extractor.extract_entities(request.text_content)
    
    evidence = Evidence(
        case_id=request.case_id,
        user_id=user_id,
        type="document",
        extracted_entities=entities,
        ocr_text=request.text_content
    )
    
    if db.db is not None:
        await db.db["evidence"].insert_one(evidence.model_dump(by_alias=True))
    
    return {"status": "success", "entities": entities}

@router.post("/generate-timeline")
async def generate_timeline(case_id: str, user_id: str = Depends(get_current_user)):
    """Generates an investigation timeline from case history."""
    from backend.app.mcp_servers.memory.server import get_case_history
    history = await get_case_history(case_id, user_id)
    
    if not history:
        return {"status": "error", "detail": "No history found"}
        
    # Mocking LLM timeline generation
    timeline = [
        TimelineEvent(case_id=case_id, time=history[0]["timestamp"], description="Incident reported by user"),
        TimelineEvent(case_id=case_id, time=history[-1]["timestamp"], description="AI analysis completed")
    ]
    
    if db.db is not None:
         for t in timeline:
             await db.db["timelines"].insert_one(t.model_dump())
             
    return {"status": "success", "timeline": [t.model_dump() for t in timeline]}
