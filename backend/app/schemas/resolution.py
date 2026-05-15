from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Dict, Any

class IncidentDimensions(BaseModel):
    asset_affected: List[str] = Field(..., description="What was compromised? e.g. 'money', 'account', 'data', 'identity', 'device', 'reputation'")
    attack_type: str = Field(..., description="Nature of the attack e.g. 'fraud', 'unauthorized_access', 'malware', 'impersonation', 'harassment', 'unknown'")
    control_authority: List[str] = Field(..., description="Entities with power to resolve (e.g., 'Bank', 'SocialMediaPlatform', 'Telecom')")
    urgency: str = Field(..., description="Severity and time-sensitivity e.g. 'low', 'medium', 'high', 'critical'")
    summary: str = Field(..., description="One sentence summary of the incident")
    prevention_tips: List[str] = Field(..., description="3 actionable tips to prevent this in future")
    incident_logic: str = Field(..., description="Brief explanation of how this attack works (mechanism)")

class ResolutionStep(BaseModel):
    step_id: str
    phase: str = Field(..., description="Phase: 'containment', 'securing', 'reporting', 'recovery', 'prevention'")
    action: str
    description: str
    authority_involved: Optional[str] = None
    is_completed: bool = False

class ResolutionStrategy(BaseModel):
    lifecycle_plan: List[ResolutionStep] = Field(..., description="Ordered list of steps across all phases")
    estimated_timeline: str

class AuthorityContact(BaseModel):
    name: str # e.g. "HDFC Bank"
    role: str # e.g. "Financial Institution"
    contact_info: Dict[str, str] # e.g. {"phone": "1930", "email": "help@hdfcbank.com"}
    required_documents: List[str]

class ConfidenceScores(BaseModel):
    scam_likelihood: float = Field(0.0, ge=0.0, le=1.0)
    attack_sophistication: float = Field(0.0, ge=0.0, le=1.0)
    recovery_probability: float = Field(0.0, ge=0.0, le=1.0)
    urgency_score: float = Field(0.0, ge=0.0, le=1.0)

class GraphNode(BaseModel):
    id: str
    type: str # 'victim', 'scammer', 'wallet', 'phone', 'url', 'bank_account', 'telegram'
    label: str
    metadata: Dict[str, Any] = {}

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str # 'targeted_by', 'paid_to', 'contacted_via', 'linked_to'

class TimelineEvent(BaseModel):
    id: str
    timestamp: str
    event_type: str # 'incident_start', 'evidence_upload', 'analysis_complete', 'action_taken'
    description: str
    impact: Optional[str] = None

class CaseState(BaseModel):
    incident_id: str
    dimensions: IncidentDimensions
    strategy: ResolutionStrategy
    authorities: List[AuthorityContact]
    confidence_metrics: ConfidenceScores = Field(default_factory=ConfidenceScores)
    graph_data: Dict[str, List] = Field(default_factory=lambda: {"nodes": [], "edges": []})
    timeline: List[TimelineEvent] = Field(default_factory=list)
    agent_traces: List[Dict[str, Any]] = Field(default_factory=list)
    current_step_index: int = 0
    status: str = Field("open", description="Status: 'open', 'in_progress', 'resolved', 'stuck'")

class IncidentRequest(BaseModel):
    description: str = Field(..., description="User's natural language description of the incident")
    evidence_ids: List[str] = Field(default_factory=list)
    user_context: Optional[Dict[str, str]] = Field(None, description="Optional context like 'country', 'bank_name', etc.")
