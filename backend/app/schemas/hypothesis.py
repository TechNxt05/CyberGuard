from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

HypothesisStatus = Literal["ACTIVE", "CONFIRMED", "DISPROVEN", "SUPERSEDED"]

class CaseHypothesis(BaseModel):
    hypothesis_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    title: str
    description: str
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradictory_evidence_ids: List[str] = Field(default_factory=list)
    confidence_score: float = 0.5
    status: HypothesisStatus = "ACTIVE"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
