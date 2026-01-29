from backend.app.schemas.resolution import CaseState
from typing import Dict

# Simple in-memory store for MVP. In production, use Redis/Postgres.
CASE_STORE: Dict[str, CaseState] = {}

def save_case_state(case: CaseState) -> str:
    """
    Saves or updates the case state in the store.
    """
    CASE_STORE[case.incident_id] = case
    return "Case saved."

def get_case_state(incident_id: str) -> CaseState | None:
    """
    Retrieves a case by ID.
    """
    return CASE_STORE.get(incident_id)
