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
