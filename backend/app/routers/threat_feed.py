from datetime import datetime

from fastapi import APIRouter, Depends

from app.db.mongodb import get_db
from app.services.memory_service import ThreatMemoryService
from app.services.rate_limit import read_only

router = APIRouter(tags=["Threat Feed"], dependencies=[Depends(read_only)])

# Curated reference material: common scam patterns in India. These are static advisories,
# not live detections, and the API labels them as such.
ADVISORIES = [
    {"id": "adv-upi-refund", "type": "UPI_FRAUD", "title": "Fake UPI refund / 'collect request' scams",
     "detail": "You never need to enter your UPI PIN to RECEIVE money. A request asking for your PIN is a payment out of your account.",
     "affectedPlatform": "UPI apps"},
    {"id": "adv-kyc", "type": "PHISHING", "title": "Bank KYC-expiry SMS with a link",
     "detail": "Banks don't block accounts over SMS links. Open your bank's app or type its website address yourself.",
     "affectedPlatform": "SMS / NetBanking"},
    {"id": "adv-digital-arrest", "type": "VISHING", "title": "'Digital arrest' calls impersonating police/CBI/customs",
     "detail": "No agency arrests anyone over a video call or asks for money to 'clear' a case. Hang up and call 1930.",
     "affectedPlatform": "Phone / WhatsApp / Skype"},
    {"id": "adv-task-jobs", "type": "INVESTMENT_FRAUD", "title": "Part-time 'like videos / rate hotels' task jobs",
     "detail": "Small early payouts build trust, then you are asked to 'invest' to unlock earnings that never come back.",
     "affectedPlatform": "WhatsApp / Telegram"},
    {"id": "adv-courier", "type": "COURIER_FRAUD", "title": "Parcel 'held at customs' with illegal items",
     "detail": "Courier companies don't transfer calls to police or ask for fees by UPI/crypto to release parcels.",
     "affectedPlatform": "Phone / WhatsApp"},
    {"id": "adv-sextortion", "type": "SEXTORTION", "title": "Sextortion emails and video calls",
     "detail": "Don't pay - payment leads to more demands. Preserve evidence and report at cybercrime.gov.in.",
     "affectedPlatform": "Email / Video calls"},
]


@router.get("/api/threat-feed")
async def get_threat_feed(db=Depends(get_db)):
    indicators = await ThreatMemoryService(db).get_recent_threats(limit=10) if db is not None else []
    return {
        "indicators": indicators,  # real: indicators seen in 2+ investigations on this platform
        "advisories": ADVISORIES,  # static reference content
        "generatedAt": datetime.utcnow().isoformat() + "Z",
    }
