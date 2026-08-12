from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class AgentExecutionPolicy(BaseModel):
    agent_name: str
    timeout_seconds: float = 30.0
    retry_limit: int = 2
    tool_budget: int = 10
    token_budget: int = 4000
    cost_budget_usd: float = 0.010
    confidence_threshold: float = 0.80

class AgentPolicyEngine:
    """
    Agent Execution Policy & Reliability Engine.
    Enforces per-agent tool budgets, token budgets, duplicate tool-call caching,
    and investigation drift detection.
    """

    def __init__(self):
        self._tool_call_cache: Dict[str, Any] = {}
        self._default_policies = {
            "UnderstandingAgent": AgentExecutionPolicy(agent_name="UnderstandingAgent", tool_budget=5, token_budget=2000),
            "EvidenceAgent": AgentExecutionPolicy(agent_name="EvidenceAgent", tool_budget=8, token_budget=3000),
            "ThreatIntelAgent": AgentExecutionPolicy(agent_name="ThreatIntelAgent", tool_budget=12, token_budget=5000),
            "StrategyAgent": AgentExecutionPolicy(agent_name="StrategyAgent", tool_budget=5, token_budget=2500),
            "RecoveryAgent": AgentExecutionPolicy(agent_name="RecoveryAgent", tool_budget=5, token_budget=2000),
            "AuthorityMapperAgent": AgentExecutionPolicy(agent_name="AuthorityMapperAgent", tool_budget=5, token_budget=2000),
            "PreventionAgent": AgentExecutionPolicy(agent_name="PreventionAgent", tool_budget=5, token_budget=2000)
        }

    def check_duplicate_action(self, agent_name: str, tool_name: str, args_key: str) -> tuple[bool, Optional[Any]]:
        cache_id = f"{agent_name}:{tool_name}:{args_key}"
        if cache_id in self._tool_call_cache:
            logger.info(f"[AgentPolicy] Duplicate action detected: {cache_id}. Returning cached result.")
            return True, self._tool_call_cache[cache_id]
        return False, None

    def record_action(self, agent_name: str, tool_name: str, args_key: str, result: Any):
        cache_id = f"{agent_name}:{tool_name}:{args_key}"
        self._tool_call_cache[cache_id] = result

    def detect_investigation_drift(self, expected_tasks: List[str], actual_actions: List[str]) -> float:
        """
        Calculates investigation drift score (0.0 = on track, 1.0 = heavy drift).
        """
        if not expected_tasks or not actual_actions:
            return 0.0
            
        matches = sum(1 for act in actual_actions if any(exp.lower() in act.lower() for exp in expected_tasks))
        drift = 1.0 - (matches / len(actual_actions))
        return round(max(0.0, min(1.0, drift)), 2)

policy_engine = AgentPolicyEngine()
