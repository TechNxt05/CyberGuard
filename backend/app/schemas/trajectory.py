from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class TrajectoryToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    output: Optional[str] = None
    success: bool = True
    latency_ms: float = 0.0

class TrajectoryStep(BaseModel):
    step_index: int
    agent_name: str
    reasoning: str
    tool_calls: List[TrajectoryToolCall] = Field(default_factory=list)
    retries: int = 0
    errors: List[str] = Field(default_factory=list)
    timestamp: str

class AuditAITrajectory(BaseModel):
    case_id: str
    task: str
    reasoning_steps: List[TrajectoryStep] = Field(default_factory=list)
    total_retries: int = 0
    errors: List[str] = Field(default_factory=list)
    recoverability_score: float = Field(0.95, ge=0.0, le=1.0, description="AuditAI recoverability confidence score")
    execution_status: str = "COMPLETED"
