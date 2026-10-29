import logging

from app.schemas.common import ScoutReport, UserProfile
from app.services.llm_provider import get_vision_llm, image_message, response_text, structured_call
from app.services.scam_knowledge import get_scam_rules, search_scam_patterns

logger = logging.getLogger(__name__)

SYSTEM = "You are a ruthlessly efficient scam detection expert. Use the provided context and rules to judge the message."

OCR_PROMPT = (
    "Extract all readable text from this screenshot. If it looks like a scam message, "
    "describe the visual context (e.g. logos, urgency, payment requests)."
)


def extract_image_text(image_base64: str, mime_type: str = "image/jpeg") -> str:
    response = get_vision_llm().invoke([image_message(OCR_PROMPT, image_base64, mime_type)])
    return response_text(response.content)


def _failed_report(reason: str) -> ScoutReport:
    # Fail closed: a security tool must never call something SAFE just because analysis broke.
    return ScoutReport(
        scam_probability=50,
        verdict="SUSPICIOUS",
        risk_score=50,
        scam_logic=f"Automated analysis could not be completed ({reason}). Treat this message as unverified.",
        consequences="Unknown - do not act on this message until you have verified it independently.",
        severity="medium",
        recommendation="Do not click links, share OTPs/PINs, or send money. Verify through the official app, website or helpline (1930 for financial fraud in India).",
        extracted_entities={},
        analysis_status="failed",
    )


def detect_scam(message: str | None, user_profile: UserProfile, image_base64: str | None = None, image_mime_type: str = "image/jpeg") -> ScoutReport:
    if image_base64:
        try:
            image_text = extract_image_text(image_base64, image_mime_type)
            message = f"{message}\n\n[Screenshot content]\n{image_text}" if message else image_text
        except Exception as e:
            logger.warning("Image analysis failed: %s", e)
            if not message:
                return _failed_report("the screenshot could not be read")

    if not message:
        return _failed_report("no content was provided")

    user = f"""
Analyze this message: "{message}"

Similar known scams from our knowledge base:
{search_scam_patterns(message)}

Known scam rules:
{get_scam_rules()}

User profile: {user_profile.model_dump()}

Fill every field. scam_probability and risk_score are 0-100. scam_logic explains EXACTLY how the trick works,
consequences explains EXACTLY what the victim could lose, recommendation gives a clear DO and DON'T.
"""
    try:
        return structured_call(SYSTEM, user, ScoutReport, temperature=0.2)
    except Exception as e:
        logger.error("Scam detection LLM call failed: %s", e)
        return _failed_report("the AI model is unavailable")
