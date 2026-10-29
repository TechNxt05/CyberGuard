import logging
from typing import List, Optional

from app.schemas.resolution import ResolutionStep
from app.services.llm_provider import atext_call, text_call

logger = logging.getLogger(__name__)


def guide_step(step: ResolutionStep) -> str:
    """Expands a single resolution step into a short micro-guide."""
    try:
        return text_call(
            "You are a patient, step-by-step technical guide.",
            f"Expand this resolution step into a micro-guide of 3-5 very short, clear sentences.\nStep: {step.description}\nAction: {step.action}",
            temperature=0.5,
        )
    except Exception as e:
        logger.warning("Guide generation failed: %s", e)
        return f"{step.action}\n{step.description}"


async def assist_form(action: str, docs: Optional[List[str]] = None) -> str:
    return await atext_call(
        "You are a legal aid assistant helping users prepare complaints.",
        f"The user needs to perform this action: {action}\nRequired documents/info typically involved: {docs or 'unknown'}\n\n"
        "Draft a template text or a checklist of evidence they need to gather before starting.",
        temperature=0.5,
    )


async def resolve_doubt(question: str, plan_summary: str) -> str:
    return await atext_call(
        "You are a reassuring cybercrime-recovery expert answering a victim's questions. Be specific and practical. "
        "Never ask for OTPs, passwords or card numbers.",
        f"User question: {question}\nContext (current plan): {plan_summary}\n\nAnswer the user.",
        temperature=0.5,
    )
