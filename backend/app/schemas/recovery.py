from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime
import uuid

ApprovalStatus = Literal["PROPOSED", "APPROVED", "REJECTED", "EXECUTED"]

class RecoveryAction(BaseModel):
    action_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    action_type: Literal["bank_freeze", "upi_block", "police_report", "password_reset", "evidence_preservation"] = "bank_freeze"
    title: str
    description: str
    recommended_by: str = "RecoveryAgent"
    approval_status: ApprovalStatus = "PROPOSED"
    approved_by: Optional[str] = None
    deadline: Optional[str] = None
    evidence_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    def approve(self, user_id: str):
        self.approval_status = "APPROVED"
        self.approved_by = user_id

    def execute(self):
        if self.approval_status != "APPROVED":
            raise ValueError("Cannot execute unapproved recovery action. Human approval required.")
        self.approval_status = "EXECUTED"
        self.completed_at = datetime.utcnow()
