import logging
import uuid

from app.schemas.resolution import IncidentDimensions, ResolutionStep, ResolutionStrategy
from app.services.llm_provider import structured_call
from app.services.playbooks import get_playbook

logger = logging.getLogger(__name__)

SYSTEM = "You are a strategic crisis manager. Create a tailored, step-by-step resolution plan for a cybercrime victim."

PHASES = ["containment", "securing", "reporting", "recovery", "prevention"]


def _playbook_strategy(playbook: dict) -> ResolutionStrategy:
    """Deterministic plan straight from the curated playbook, used when the LLM is unavailable."""
    steps = [
        ResolutionStep(step_id=str(uuid.uuid4())[:8], phase=phase, action=action, description=action)
        for phase in PHASES
        for action in playbook.get(phase, [])
    ]
    return ResolutionStrategy(lifecycle_plan=steps, estimated_timeline="Varies - start with the containment steps immediately.")


def create_strategy(dimensions: IncidentDimensions, research_context: str = "") -> ResolutionStrategy:
    playbook = get_playbook(dimensions.attack_type)
    user = f"""
Incident dimensions: {dimensions.model_dump()}

Web search snippets (use only clearly relevant, official links; ignore the rest):
{research_context or "none"}

Generic playbook for this attack type: {playbook}

Break the playbook into specific, actionable steps for this user. Give each step a unique step_id and one
phase from {PHASES}. Estimate the overall timeline.
"""
    try:
        strategy = structured_call(SYSTEM, user, ResolutionStrategy, temperature=0.3)
        if strategy.lifecycle_plan:
            return strategy
    except Exception as e:
        logger.error("Strategy generation failed: %s", e)
    return _playbook_strategy(playbook if isinstance(playbook, dict) else {})
