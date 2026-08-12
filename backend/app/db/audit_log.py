from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

class AuditLogEntry(BaseModel):
    entry_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str
    organization_id: str = "default_org"
    action: str  # e.g. CASE_CREATED, EVIDENCE_UPLOADED, REPORT_GENERATED, ACTION_APPROVED
    case_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    ip_address: Optional[str] = "127.0.0.1"

class AuditLogger:
    """
    Append-Only Audit Log Service.
    Records all sensitive actions and security events for auditability.
    """

    def __init__(self):
        self._logs: List[AuditLogEntry] = []

    def log_action(self, user_id: str, action: str, case_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> AuditLogEntry:
        entry = AuditLogEntry(
            user_id=user_id,
            action=action,
            case_id=case_id,
            details=details or {}
        )
        self._logs.append(entry)
        logger.info(f"[AuditLog] {action} by User {user_id} on Case {case_id}")
        return entry

    def get_audit_trail(self, case_id: Optional[str] = None) -> List[AuditLogEntry]:
        if case_id:
            return [l for l in self._logs if l.case_id == case_id]
        return self._logs

audit_logger = AuditLogger()
