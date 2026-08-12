from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

class CaseRevision(BaseModel):
    revision_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    previous_goal: str
    new_goal: str
    previous_hypothesis: Optional[str] = None
    new_hypothesis: Optional[str] = None
    triggering_evidence: List[str] = Field(default_factory=list)
    reason: str
    affected_agents: List[str] = Field(default_factory=list)
    affected_tasks: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str = "system"
