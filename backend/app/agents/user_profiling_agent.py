import logging

from app.schemas.common import UserProfile
from app.services.llm_provider import structured_call

logger = logging.getLogger(__name__)

SYSTEM = "You are an expert behavioral analyst helping to protect users from scams. Infer the likely profile of the person who received this message."


def profile_user(message: str, source: str) -> UserProfile:
    try:
        return structured_call(SYSTEM, f"Message: {message}\nSource: {source}", UserProfile, temperature=0.3)
    except Exception as e:
        # Profiling only tunes the tone of the explanation, so a neutral default is safe here.
        logger.warning("Profiling failed, using default profile: %s", e)
        return UserProfile(user_type="adult")
