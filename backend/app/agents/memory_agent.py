import logging

from app.schemas.common import ScamAnalysisResult
from app.services.case_store import store_scam_case

logger = logging.getLogger(__name__)


async def update_memory(result: ScamAnalysisResult) -> None:
    """Stores the analysed report for later review. Never fails the user's request."""
    try:
        await store_scam_case(result)
    except Exception as e:
        logger.warning("Could not store scam report: %s", e)
