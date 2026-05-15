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

from backend.app.schemas.confidence import ConfidenceRequest, ConfidenceResponse
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from pydantic import ValidationError

@router.post("/confidence", response_model=ConfidenceResponse)
async def analyze_confidence(req: ConfidenceRequest):
    """Calculates threat confidence, urgency, and priority actions using Gemini 1.5 Flash."""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.2)
        prompt = f"""
You are a Cyber Threat Intelligence Expert. Analyze the following incident and return ONLY valid JSON matching the exact schema below. Do not include markdown code blocks or any other text.

Schema:
{{
  "scamLikelihood": int (0-100),
  "attackSophistication": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "sophisticationScore": int (0-100),
  "recoveryProbability": int (0-100),
  "urgencyLevel": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "urgencyReason": "string explaining why",
  "timeToAct": "string suggesting timeframe",
  "priorityActions": [
    {{"action": "string", "deadline": "string", "impact": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL"}}
  ],
  "riskFactors": ["string"],
  "mitigatingFactors": ["string"]
}}

Incident Description: {req.incidentDescription}
Extracted Entities: {json.dumps(req.extractedEntities)}
"""
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Remove markdown if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed_json = json.loads(content.strip())
        return ConfidenceResponse(**parsed_json)
    except Exception as e:
        # Fallback response in case of error
        return ConfidenceResponse(
            scamLikelihood=80,
            attackSophistication="HIGH",
            sophisticationScore=75,
            recoveryProbability=50,
            urgencyLevel="HIGH",
            urgencyReason=f"System error during analysis, assuming high risk. Error: {str(e)[:50]}",
            timeToAct="Act Immediately",
            priorityActions=[{"action": "Contact Bank", "deadline": "Now", "impact": "CRITICAL"}],
            riskFactors=["Unknown automated threat"],
            mitigatingFactors=[]
        )

from backend.app.schemas.timeline import TimelineRequest, TimelineResponse
import uuid

@router.post("/timeline", response_model=TimelineResponse)
async def analyze_timeline(req: TimelineRequest):
    """Reconstructs the attack timeline."""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1)
        prompt = f"""
You are a Cyber Forensics Expert. Reconstruct a chronological timeline of the attack from the incident description.
Return ONLY valid JSON matching this exact schema:
{{
  "events": [
    {{
      "id": "string",
      "timestamp": "ISO 8601 string",
      "eventType": "reconnaissance" | "initial_access" | "execution" | "exfiltration" | "impact",
      "description": "string",
      "impact": "string",
      "relativeTime": "e.g. T+0, T+5 mins, T+2 hours"
    }}
  ]
}}

Incident Description: {req.incidentDescription}
"""
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed_json = json.loads(content.strip())
        
        # Ensure IDs exist
        for ev in parsed_json.get("events", []):
            if not ev.get("id"):
                ev["id"] = str(uuid.uuid4())
                
        return TimelineResponse(**parsed_json)
    except Exception as e:
        import datetime
        return TimelineResponse(
            events=[
                {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
                    "eventType": "impact",
                    "description": "Fallback timeline generated due to error.",
                    "impact": "Unknown",
                    "relativeTime": "T+0"
                }
            ]
        )

from backend.app.schemas.graph import GraphRequest, GraphResponse

@router.post("/graph", response_model=GraphResponse)
async def analyze_graph(req: GraphRequest):
    """Generates an investigation graph mapping entities and relations."""
    try:
        # Use Gemini 1.5 Pro for complex graph extraction
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", temperature=0.1)
        prompt = f"""
You are a Cyber Threat Intelligence analyst. Extract a relationship graph of the entities involved in this cyber incident.
Return ONLY valid JSON matching this exact schema:
{{
  "nodes": [
    {{
      "id": "string (unique)",
      "type": "victim" | "threat_actor" | "mule_account" | "url" | "ip" | "wallet" | "email",
      "label": "string",
      "metadata": {{"key": "value"}}
    }}
  ],
  "edges": [
    {{
      "id": "string",
      "source": "node_id",
      "target": "node_id",
      "label": "string (e.g. 'targeted', 'transferred_to', 'hosted_on')",
      "type": "animated"
    }}
  ]
}}

Incident Description: {req.incidentDescription}
Extracted Entities: {json.dumps(req.extractedEntities)}
"""
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
            
        parsed_json = json.loads(content.strip())
        return GraphResponse(**parsed_json)
    except Exception as e:
        return GraphResponse(
            nodes=[
                {"id": "n_victim", "type": "victim", "label": "Victim", "metadata": {}},
                {"id": "n_threat", "type": "threat_actor", "label": "Unknown Attacker", "metadata": {}}
            ],
            edges=[
                {"id": "e_1", "source": "n_victim", "target": "n_threat", "label": "targeted_by", "type": "animated"}
            ]
        )
