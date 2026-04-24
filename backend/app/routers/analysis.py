from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import base64
from backend.app.auth.clerk_auth import get_current_user

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])

@router.post("/analyze-image")
async def analyze_image(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    """Analyzes an uploaded image for cyber threats."""
    from backend.app.services.vision_engine import VisionEngine
    try:
        contents = await file.read()
        base64_img = base64.b64encode(contents).decode("utf-8")
        
        vision = VisionEngine()
        result = await vision.analyze_screenshot(base64_img)
        
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-audio")
async def analyze_audio(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    """Analyzes audio for deepfake probabilities and scam scripts."""
    from backend.app.services.audio_engine import AudioEngine
    try:
        contents = await file.read()
        
        audio = AudioEngine()
        result = await audio.analyze_audio(contents, file.filename)
        
        return {"status": "success", "analysis": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/analyze-video")
async def analyze_video(file: UploadFile = File(...), user_id: str = Depends(get_current_user)):
    """Analyzes video for deepfake manipulation and extracts audio frames."""
    raise HTTPException(status_code=501, detail="Video analysis coming soon")
