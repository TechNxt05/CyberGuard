import logging

from app.schemas.common import ScoutReport, UserProfile
from app.services.llm_provider import get_vision_llm, image_message, language_instruction, response_text, structured_call
from app.services.scam_knowledge import get_scam_rules, search_scam_patterns
from app.services.url_intel import check_urls_in_text, risk_floor

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

    url_checks = check_urls_in_text(message)
    evidence = "\n".join(f"- {c['url']}: {c['verdict']} ({'; '.join(c['signals']) or 'no signals'})" for c in url_checks)

    user = f"""
Analyze this message: "{message}"

Similar known scams from our knowledge base:
{search_scam_patterns(message)}

Known scam rules:
{get_scam_rules()}

User profile: {user_profile.model_dump()}

Automated link checks (reliable facts, weigh them heavily):
{evidence or "No links in the message."}

Fill every field. scam_probability and risk_score are 0-100. scam_logic explains EXACTLY how the trick works,
consequences explains EXACTLY what the victim could lose, recommendation gives a clear DO and DON'T.
"""
    try:
        report = structured_call(SYSTEM, user + language_instruction(user_profile.language), ScoutReport, temperature=0.2)
    except Exception as e:
        logger.error("Scam detection LLM call failed: %s", e)
        report = _failed_report("the AI model is unavailable")
    return apply_url_evidence(report, url_checks)


_VERDICT_RANK = {"SAFE": 0, "SUSPICIOUS": 1, "SCAM": 2}


def apply_url_evidence(report: ScoutReport, url_checks: list[dict]) -> ScoutReport:
    """Hard evidence sets a floor the model can't argue below (e.g. a days-old look-alike bank domain)."""
    report.url_checks = url_checks
    floor = risk_floor(url_checks)
    if floor:
        min_risk, min_verdict = floor
        report.risk_score = max(report.risk_score, min_risk)
        report.scam_probability = max(report.scam_probability, float(min_risk))
        if _VERDICT_RANK[report.verdict] < _VERDICT_RANK[min_verdict]:
            report.verdict = min_verdict
        if report.severity in ("safe", "low", "medium") and min_risk >= 85:
            report.severity = "high"
    return report
