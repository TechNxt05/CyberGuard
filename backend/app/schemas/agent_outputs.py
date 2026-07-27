from pydantic import BaseModel, Field, ConfigDict
from typing import List, Literal, Dict, Any, Optional

class UnderstandingAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    case_type: Literal["fraud", "unauthorized_access", "malware", "impersonation", "harassment", "unknown"] = Field(
        ..., description="Categorization of the incident type"
    )
    victim_profile: Dict[str, Any] = Field(
        default_factory=dict, description="Profile information of the victim"
    )
    extracted_indicators: List[str] = Field(
        default_factory=list, description="Extracted indicators of compromise (IOCs)"
    )
    attack_timeline: List[Dict[str, Any]] = Field(
        default_factory=list, description="Reconstructed chronological attack timeline"
    )
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Agent confidence score between 0.0 and 1.0"
    )
    missing_evidence: List[str] = Field(
        default_factory=list, description="Evidence gaps identified during understanding phase"
    )

class EvidenceAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    extracted_entities: Dict[str, List[str]] = Field(
        default_factory=dict, description="Extracted entity dictionaries by category"
    )
    ocr_confidence: float = Field(
        0.95, ge=0.0, le=1.0, description="OCR extraction confidence score"
    )
    evidence_quality: Literal["high", "medium", "low"] = Field(
        "high", description="Overall quality score of provided evidence"
    )
    flagged_patterns: List[str] = Field(
        default_factory=list, description="Suspicious patterns detected in evidence"
    )

class ThreatIntelAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    matched_patterns: List[Dict[str, Any]] = Field(
        default_factory=list, description="Known threat patterns matching current incident"
    )
    known_threat_matches: List[Dict[str, Any]] = Field(
        default_factory=list, description="Entities matching historical threat intelligence database"
    )
    research_summary: str = Field(
        ..., description="Synthesized research findings from threat intelligence sources"
    )
    confidence_score: float = Field(
        0.85, ge=0.0, le=1.0, description="Threat intel confidence score"
    )

class StrategyAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    lifecycle_plan: List[Dict[str, Any]] = Field(
        default_factory=list, description="Actionable resolution steps ordered by priority"
    )
    estimated_timeline: str = Field(
        ..., description="Estimated timeframe for incident resolution"
    )
    priority_phase: str = Field(
        "containment", description="Current highest priority resolution phase"
    )

class RecoveryAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    current_guide: str = Field(
        ..., description="Step-by-step assistant guidance for immediate recovery"
    )
    immediate_actions: List[str] = Field(
        default_factory=list, description="List of immediate emergency actions for victim"
    )
    contact_targets: List[str] = Field(
        default_factory=list, description="Key target entities to contact (e.g. Bank helpline, Cybercell)"
    )

class AuthorityMapperAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    mapped_authorities: List[Dict[str, Any]] = Field(
        default_factory=list, description="Relevant law enforcement and regulatory authorities mapped"
    )
    status: str = Field(
        "in_progress", description="Status of authority mapping and FIR generation"
    )
    jurisdiction_notes: str = Field(
        "", description="Notes on legal jurisdiction and reporting protocols"
    )

class PreventionAgentOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    prevention_tips: List[str] = Field(
        default_factory=list, description="Actionable prevention tips for long-term protection"
    )
    insights: List[str] = Field(
        default_factory=list, description="Key security insights gained from investigation"
    )
    risk_mitigation_score: float = Field(
        0.9, ge=0.0, le=1.0, description="Estimated risk mitigation percentage"
    )

class AgentValidationWrapper:
    """
    Helper for validating agent outputs with single retry and human escalation fallback.
    """
    @staticmethod
    def validate_or_escalate(output_data: Dict[str, Any], schema_cls: type, agent_name: str) -> tuple[Any, bool, Optional[str]]:
        try:
            validated = schema_cls.model_validate(output_data)
            return validated, True, None
        except Exception as err:
            error_msg = f"Agent {agent_name} output validation failed: {str(err)}"
            return None, False, error_msg
