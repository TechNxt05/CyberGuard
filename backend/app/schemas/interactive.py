from pydantic import BaseModel, Field
from typing import Optional, List

class DoubtRequest(BaseModel):
    incident_id: str
    question: str

class DoubtResponse(BaseModel):
    answer: str

class FormAssistRequest(BaseModel):
    incident_id: str
    action_item: str

class FormAssistResponse(BaseModel):
    guidance: str
    checklist: List[str]
