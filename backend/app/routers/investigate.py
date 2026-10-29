import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.auth.clerk_auth import get_current_user
from app.db.mongodb import get_db
from app.schemas.common import MAX_IMAGE_BASE64_CHARS, MAX_TEXT_CHARS
from app.services.entity_extraction import extract_entities
from app.services.memory_service import ThreatMemoryService
from app.services.rate_limit import llm_light

logger = logging.getLogger(__name__)

router = APIRouter()


class InvestigationRequest(BaseModel):
    message: str = Field("", max_length=MAX_TEXT_CHARS)
    sessionId: str = Field(..., min_length=1, max_length=100)
    imageBase64: Optional[str] = Field(None, max_length=MAX_IMAGE_BASE64_CHARS)
    imageMimeType: Optional[str] = Field("image/jpeg", pattern=r"^image/(png|jpeg|jpg|webp|gif)$")


@router.post("/api/investigate", dependencies=[Depends(llm_light)])
async def run_investigation(req: InvestigationRequest, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    """
    Extracts fraud indicators (text + optional screenshot), checks them against threat memory,
    and records them. Requires sign-in so every memory write is attributable to a real user.
    """
    text = req.message
    image_text = None
    if req.imageBase64:
        from app.agents.scam_detection_agent import extract_image_text
        try:
            image_text = await run_in_threadpool(extract_image_text, req.imageBase64, req.imageMimeType or "image/jpeg")
            text = f"{text}\n{image_text}"
        except Exception as e:
            logger.warning("Screenshot text extraction failed: %s", e)

    if not text.strip():
        raise HTTPException(status_code=400, detail="Describe the incident or attach a readable screenshot.")

    extracted = extract_entities(text)
    if db is None:
        return {"sessionId": req.sessionId, "extracted_entities": extracted, "image_text": image_text, "known_threats": []}

    memory_service = ThreatMemoryService(db)
    known_threats = await memory_service.check_entities(extracted)  # check BEFORE storing so we don't match ourselves
    if any(extracted.values()):
        await memory_service.store_entities(extracted, case_id=req.sessionId, crime_type="reported_incident", reporter_id=user_id)

    return {
        "sessionId": req.sessionId,
        "extracted_entities": extracted,
        "image_text": image_text,
        "known_threats": known_threats,
    }
