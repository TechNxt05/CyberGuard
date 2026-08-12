from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
import uuid
import hashlib

EvidenceType = Literal[
    "screenshot",
    "pdf",
    "bank_statement",
    "chat_export",
    "whatsapp_screenshot",
    "email",
    "url",
    "audio",
    "video",
    "image",
    "transaction_record",
    "document",
    "text"
]

IntegrityStatus = Literal["ORIGINAL", "DERIVED", "USER_MODIFIED", "AI_DERIVED"]

ProvenanceAction = Literal[
    "uploaded",
    "parsed",
    "OCR_processed",
    "analyzed",
    "modified",
    "derived",
    "exported"
]

class EvidenceProvenanceRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    action: ProvenanceAction
    processor_version: str = "CyberGuard_v3.0"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    performed_by: str = "system"
    notes: Optional[str] = None
    input_hash: Optional[str] = None
    output_hash: Optional[str] = None

VerificationStatus = Literal[
    "VERIFIED",
    "PARTIALLY_VERIFIED",
    "UNVERIFIED",
    "CONTRADICTED",
    "INSUFFICIENT_EVIDENCE"
]

class EvidenceClaim(BaseModel):
    claim_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    claim_text: str
    evidence_id: str
    verification_status: VerificationStatus = "UNVERIFIED"
    supporting_evidence_ids: List[str] = Field(default_factory=list)
    contradictory_evidence_ids: List[str] = Field(default_factory=list)
    confidence: float = 0.5
    notes: Optional[str] = None

class EvidenceItem(BaseModel):
    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    type: EvidenceType = "screenshot"
    source: str = "user_upload"
    original_hash: str  # SHA-256
    current_hash: str   # SHA-256
    mime_type: str = "image/png"
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    content_location: str = ""
    ocr_text: Optional[str] = None
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    integrity_status: IntegrityStatus = "ORIGINAL"
    confidence: float = 0.95
    parent_evidence_id: Optional[str] = None
    provenance_chain: List[EvidenceProvenanceRecord] = Field(default_factory=list)

    @staticmethod
    def compute_sha256(content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()
