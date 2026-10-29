import logging
from typing import Dict, Optional

from app.schemas.resolution import IncidentDimensions
from app.services.llm_provider import structured_call

logger = logging.getLogger(__name__)

SYSTEM = (
    "You are an expert cyber incident classifier. Extract the 5 universal dimensions of a cybercrime "
    "from the user's description, 3 prevention tips, a brief explanation of the attack mechanism, and the "
    "specific control authorities (e.g. 'Bank', 'Instagram', 'Police') who can act on it."
)


def understand_incident(description: str, context: Optional[Dict] = None) -> IncidentDimensions:
    try:
        return structured_call(SYSTEM, f"User description: {description}\nUser context: {context or {}}", IncidentDimensions, temperature=0)
    except Exception as e:
        logger.error("Incident understanding failed: %s", e)
        return IncidentDimensions(
            asset_affected=["unknown"],
            attack_type="unknown",
            control_authority=["Cyber Crime Portal"],
            urgency="high",
            summary="We could not automatically analyse this incident. Please follow the general steps below.",
            prevention_tips=["Never share OTPs, PINs or passwords", "Enable 2FA on important accounts", "Verify requests through official channels"],
            incident_logic="Automated analysis was unavailable.",
        )
