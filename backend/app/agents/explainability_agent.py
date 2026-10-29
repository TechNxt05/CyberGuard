import logging

from app.schemas.common import ActionPlan, Advice, Explanation, ScoutReport, UserProfile
from app.services.llm_provider import UNTRUSTED_NOTE, language_instruction, structured_call, untrusted
from app.services.official_sources import sanitize_links

logger = logging.getLogger(__name__)

SYSTEM = (
    "You are a cyber-guardian angel. You explain technical risks to normal people and give concrete, "
    "actionable safety steps. Be comforting but firm if it is a scam. Only mention official websites and helplines "
    "(e.g. cybercrime.gov.in, 1930). " + UNTRUSTED_NOTE
)


def generate_advice(scout_report: ScoutReport, user_profile: UserProfile, research_context: str = "") -> Advice:
    """Explanation + action plan in a single LLM call (previously two) to stay within free-tier limits."""
    user = f"""
Scout verdict: {scout_report.verdict} (risk {scout_report.risk_score}/100)
Patterns: {", ".join(scout_report.detected_patterns) or "none listed"}
How it works: {scout_report.scam_logic}

Web search snippets about this pattern (may be empty or irrelevant - only cite them if they clearly match):
{untrusted(research_context)}

The user is: type={user_profile.user_type}, language={user_profile.language}, preferred style={user_profile.explanation_style}.

Write the explanation in that language and style. If the web snippets clearly show this scam is widely reported, say so.
The action plan should have 3-4 short DO/DON'T steps; if it is a scam include blocking/reporting instructions.
"""
    try:
        advice = structured_call(SYSTEM, user + language_instruction(user_profile.language), Advice, temperature=0.5)
        advice.explanation.simple_explanation = sanitize_links(advice.explanation.simple_explanation)
        advice.action_plan.steps = [sanitize_links(step) for step in advice.action_plan.steps]
        if advice.action_plan.blocking_instructions:
            advice.action_plan.blocking_instructions = sanitize_links(advice.action_plan.blocking_instructions)
        return advice
    except Exception as e:
        logger.error("Advice generation failed: %s", e)
        return Advice(
            explanation=Explanation(simple_explanation=scout_report.scam_logic, trust_score=0),
            action_plan=ActionPlan(steps=[scout_report.recommendation], blocking_instructions=None),
        )
