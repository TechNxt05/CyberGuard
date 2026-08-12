from pydantic import BaseModel, Field
from typing import List, Dict, Any, Callable, Optional, Literal
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

InvestigationEventType = Literal[
    "EvidenceUploaded",
    "EntityDetected",
    "RepeatThreatDetected",
    "HypothesisChanged",
    "AgentFailed",
    "CaseEscalated",
    "RecoveryActionRequired",
    "AuthorityActionRequired"
]

class InvestigationEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    event_type: InvestigationEventType
    source: str = "system"
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    confidence: float = 0.90

class InvestigationEventBus:
    """
    Event Bus for Event-Driven Cyber Investigations.
    Publishes structured events to subscribers and maintains an append-only event log.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[InvestigationEvent], None]]] = {}
        self._event_log: List[InvestigationEvent] = []

    def subscribe(self, event_type: str, callback: Callable[[InvestigationEvent], None]):
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)

    def publish(self, event: InvestigationEvent):
        self._event_log.append(event)
        logger.info(f"[EventBus] Published {event.event_type} for Case {event.case_id} (Severity: {event.severity})")

        subscribers = self._subscribers.get(event.event_type, [])
        for cb in subscribers:
            try:
                cb(event)
            except Exception as e:
                logger.error(f"[EventBus] Subscriber error on {event.event_type}: {e}")

    def get_event_log(self, case_id: Optional[str] = None) -> List[InvestigationEvent]:
        if case_id:
            return [e for e in self._event_log if e.case_id == case_id]
        return self._event_log

event_bus = InvestigationEventBus()
