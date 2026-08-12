from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid

class EvidenceManifestItem(BaseModel):
    evidence_id: str
    filename: str
    sha256_hash: str
    evidence_type: str
    timestamp: str
    source: str
    processing_version: str = "CyberGuard_v3.0"

class LegalEvidencePackage(BaseModel):
    package_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_id: str
    package_version: str = "1.0.0"
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    generator_version: str = "CyberGuardAI_C6_ReportEngine_v3.0"
    
    executive_summary: str
    incident_description: str
    victim_statement: str
    evidence_manifest: List[EvidenceManifestItem] = Field(default_factory=list)
    extracted_entities: Dict[str, List[str]] = Field(default_factory=dict)
    transaction_summary: List[Dict[str, Any]] = Field(default_factory=list)
    attack_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    hypotheses: List[Dict[str, Any]] = Field(default_factory=list)
    recovery_actions: List[Dict[str, Any]] = Field(default_factory=list)
    authority_referral_sheet: Dict[str, Any] = Field(default_factory=dict)
    digital_signature: str = ""
