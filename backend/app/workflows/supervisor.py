import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class SwarmSupervisor:
    """
    Real-time supervisor guardrail for subagent delegation depth and spawn count.
    Prevents runaway multi-agent loops and halts execution if thresholds are breached.
    """
    def __init__(self, max_depth: int = 3, max_spawns: int = 5):
        self.max_depth = max_depth
        self.max_spawns = max_spawns

    def check_guardrails(self, case_state: Any) -> tuple[bool, str]:
        """
        Evaluates current spawn count & depth against hard limits.
        Returns (is_allowed, reason).
        """
        current_depth = getattr(case_state, "delegation_depth", 0)
        current_spawns = getattr(case_state, "spawn_count", 0)
        
        if current_depth > self.max_depth:
            msg = f"Guardrail breach: delegation depth {current_depth} exceeds limit {self.max_depth}"
            logger.warning(msg)
            setattr(case_state, "human_escalation_required", True)
            setattr(case_state, "status", "escalated")
            return False, msg
            
        if current_spawns > self.max_spawns:
            msg = f"Guardrail breach: active spawn count {current_spawns} exceeds limit {self.max_spawns}"
            logger.warning(msg)
            setattr(case_state, "human_escalation_required", True)
            setattr(case_state, "status", "escalated")
            return False, msg
            
        return True, "OK"

    def record_spawn(self, case_state: Any, depth_increment: int = 1):
        setattr(case_state, "spawn_count", getattr(case_state, "spawn_count", 0) + 1)
        setattr(case_state, "delegation_depth", max(getattr(case_state, "delegation_depth", 0), depth_increment))

supervisor = SwarmSupervisor()
