from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
import re
from backend.app.services.memory_service import ThreatMemoryService
from backend.app.db.mongodb import get_db

router = APIRouter()

class InvestigationRequest(BaseModel):
    message: str
    sessionId: str
    imageBase64: Optional[str] = None
    imageMimeType: Optional[str] = "image/jpeg"
    isDemoCase: Optional[bool] = False
    demoCaseId: Optional[str] = None

def extract_preliminary_entities(text: str) -> dict:
    """
    Fast regex-based entity extraction for memory lookup.
    Runs before the full Vision OCR pipeline.
    No LLM needed.
    """
    entities = {
        "upi_id": [],
        "phone_number": [],
        "url": [],
        "email": [],
        "wallet_address": []
    }
    if not text:
        return entities

    # UPI IDs: pattern@provider
    upi_pattern = r'\b[\w.-]+@(?:ybl|paytm|upi|okaxis|okhdfcbank|oksbi|okicici|apl|ibl|pingpay|slice)\b'
    upis = re.findall(upi_pattern, text, re.IGNORECASE)
    if upis:
        entities["upi_id"] = list(set(upis))

    # Phone numbers: Indian 10-digit
    phone_pattern = r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, text)
    if phones:
        entities["phone_number"] = list(set([re.sub(r'[\s-]', '', p) for p in phones]))

    # URLs
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    if urls:
        entities["url"] = list(set(urls))

    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        entities["email"] = list(set(emails))

    # Crypto wallet addresses (Bitcoin: 26-35 chars starting with 1/3/bc1)
    wallet_pattern = r'\b(?:1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b'
    wallets = re.findall(wallet_pattern, text)
    if wallets:
        entities["wallet_address"] = list(set(wallets))

    return entities

# Static pre-loaded demo case entity mapping
DEMO_ENTITIES = {
    "demo-upi-001": {
        "crime_type": "financial_fraud",
        "entities": {
            "upi_id": ["pay.refund8821@ybl", "support.gpay991@paytm"],
            "phone_number": ["9876543210"],
            "url": ["gpay-refund-portal.xyz/claim"],
            "email": [],
            "wallet_address": []
        }
    },
    "demo-phish-002": {
        "crime_type": "phishing",
        "entities": {
            "upi_id": [],
            "phone_number": [],
            "url": ["sbi-kyc-update.in/verify", "sbi-netbanking.co/login"],
            "email": [],
            "wallet_address": []
        }
    },
    "demo-sext-003": {
        "crime_type": "sextortion",
        "entities": {
            "upi_id": [],
            "phone_number": [],
            "url": [],
            "email": ["secure.warning@proton.me"],
            "wallet_address": ["1A1zP1eP5QGefi2DMPTfTL5SLmv7Divf"]
        }
    }
}

@router.post("/api/investigate")
async def run_investigation(req: InvestigationRequest, db=Depends(get_db)):
    try:
        memory_service = ThreatMemoryService(db)

        # 1. Extract preliminary entities from the message
        extracted = extract_preliminary_entities(req.message)
        crime_type = "general_threat"

        # 2. If it is a demo case, merge standard demo case entities
        if req.isDemoCase and req.demoCaseId in DEMO_ENTITIES:
            demo_info = DEMO_ENTITIES[req.demoCaseId]
            crime_type = demo_info["crime_type"]
            for etype, evalues in demo_info["entities"].items():
                if etype not in extracted:
                    extracted[etype] = []
                extracted[etype] = list(set(extracted[etype] + evalues))

        # 3. Check memory BEFORE running full pipeline
        known_threats = await memory_service.check_entities(extracted)

        # 4. Run/Simulate the investigation pipeline
        # (This mocks/orchestrates the response and persists extracted entities)
        # Store ALL extracted entities AFTER pipeline completes
        has_entities = any(len(values) > 0 for values in extracted.values())
        if has_entities:
            await memory_service.store_entities(
                entities=extracted,
                case_id=req.sessionId,
                crime_type=crime_type
            )

        # Return response with associated known threats
        return {
            "sessionId": req.sessionId,
            "understanding": {"status": "complete", "crime_type": crime_type},
            "evidence": {
                "status": "complete",
                "extracted_entities": extracted
            },
            "confidence": {},
            "timeline": {},
            "graph": {},
            "strategy": {"status": "complete"},
            "recovery": {"status": "complete"},
            "authorityMap": {"status": "complete"},
            "prevention": {"status": "complete"},
            "known_threats": known_threats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/evaluation/swarm-metrics")
async def get_swarm_evaluation_metrics():
    from backend.app.evaluation.agent_evaluator import evaluator
    sample_exec = {
        "incident_id": str(uuid.uuid4()),
        "description": "Suspicious WhatsApp message claiming lottery win requiring UPI payment",
        "user_context": {"country": "India", "bank": "HDFC"}
    }
    return evaluator.evaluate_full_swarm(sample_exec)

