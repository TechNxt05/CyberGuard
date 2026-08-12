from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid

TaskStatus = Literal["PENDING", "RUNNING", "COMPLETED", "FAILED", "CANCELLED"]

class InvestigationTask(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    agent_type: str  # e.g. UnderstandingAgent, EvidenceAgent, ThreatIntelAgent, etc.
    objective: str
    priority: int = 1  # 1 = Highest, 5 = Lowest
    dependencies: List[str] = Field(default_factory=list)  # List of prerequisite task_ids
    status: TaskStatus = "PENDING"
    input_evidence: List[str] = Field(default_factory=list)
    required_tools: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    failure_reason: Optional[str] = None
    confidence: float = 0.0
    result_data: Dict[str, Any] = Field(default_factory=dict)
