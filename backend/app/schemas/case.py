from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    label: str
    description: Optional[str] = None
    status: Literal["pending", "in_progress", "completed", "blocked"] = "pending"
    source: Literal["agent", "user"] = "agent"
    action_link: Optional[str] = None
    action_type: Optional[Literal["link", "call", "info"]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CaseMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    user_id: str
    sender: Literal["user", "system", "agent"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Case(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    title: str = "New Incident"
    incident_summary: Optional[str] = None
    attack_type: Optional[str] = None
    incident_logic: Optional[str] = None
    prevention_tips: List[str] = []
    status: Literal["active", "resolved", "closed"] = "active"
    current_phase: str = "intake" # intake, strategy, execution, verification
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True

class Evidence(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    user_id: str
    type: Literal["image", "audio", "video", "document"]
    extracted_entities: dict = Field(default_factory=dict)
    ocr_text: Optional[str] = None
    deepfake_score: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class TimelineEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    time: str
    description: str
    source: str = "inferred"

class LegalDraft(BaseModel):
    draft_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    type: Literal["fir", "bank", "cybercrime"]
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ScamPattern(BaseModel):
    id: str = Field(alias="_id", default_factory=lambda: str(uuid.uuid4()))
    pattern_text: str
    scam_type: str
    embedding: Optional[List[float]] = None
    severity: str
