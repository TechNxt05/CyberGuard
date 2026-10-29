from pydantic import BaseModel, Field
from typing import List, Optional

class TimelineEvent(BaseModel):
    id: str = ""
    timestamp: str = ""  # ISO format when known
    eventType: str
    description: str
    impact: Optional[str] = None
    relativeTime: Optional[str] = None  # e.g. "T+10 mins"

class TimelineResponse(BaseModel):
    events: List[TimelineEvent]

class TimelineRequest(BaseModel):
    incidentDescription: str = Field(..., min_length=3, max_length=8000)
