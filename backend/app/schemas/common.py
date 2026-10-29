from pydantic import BaseModel, Field
from typing import List, Optional, Literal

# Request size limits keep a single caller from exhausting free-tier LLM quotas or Render's 512 MB RAM.
MAX_TEXT_CHARS = 8000
MAX_IMAGE_BASE64_CHARS = 7_000_000  # ~5 MB image

class AnalysisRequest(BaseModel):
    message: Optional[str] = Field(None, max_length=MAX_TEXT_CHARS, description="The suspicious message text, call summary, or offer content.")
    image_base64: Optional[str] = Field(None, max_length=MAX_IMAGE_BASE64_CHARS, description="Base64 encoded image string if screenshot is provided.")
    image_mime_type: Optional[str] = Field("image/jpeg", pattern=r"^image/(png|jpeg|jpg|webp|gif)$")
    source: Optional[str] = Field("unknown", max_length=50, description="Source of the message (e.g., whatsapp, sms, call, email)")

class UserProfile(BaseModel):
    user_type: Literal["student", "adult", "elderly", "tech_savvy"] = Field(..., description="Inferred age group or persona")
    language: Literal["hi", "en", "hinglish"] = Field("en", description="Preferred language")
    risk_sensitivity: Literal["low", "medium", "high"] = Field("medium", description="User's likely sensitivity to risk")
    explanation_style: Literal["simple", "technical", "detailed"] = Field("simple", description="How to explain things to this user")

class ScoutReport(BaseModel):
    scam_probability: float = Field(..., description="Probability of being a scam (0-100)")
    verdict: Literal["SAFE", "SUSPICIOUS", "SCAM"] = Field(..., description="Final verdict")
    detected_patterns: List[str] = Field(default_factory=list, description="List of scam patterns found")
    risk_score: int = Field(..., description="0-100 risk score")
    scam_logic: str = Field(..., description="Explanation of the mechanism used (e.g., 'Creates false urgency')")
    consequences: str = Field(..., description="Potential impact (e.g., 'Financial loss, Identity theft')")
    severity: Literal["critical", "high", "medium", "low", "safe"] = Field(..., description="Severity level")
    recommendation: str = Field(..., description="Clear action item for the user")
    extracted_entities: dict = Field(default_factory=dict, description="Key details extracted (Date, Amount, URL, etc.)")
    analysis_status: Literal["ok", "failed"] = Field("ok", description="'failed' when automated analysis could not run; the verdict is then a cautious default, not a judgement")

class Explanation(BaseModel):
    simple_explanation: str = Field(..., description="A simple, jargon-free explanation")
    trust_score: int = Field(..., description="A score indicating how trustworthy the explanation feels")

class ActionPlan(BaseModel):
    steps: List[str] = Field(..., description="Immediate DO/DON'T steps")
    blocking_instructions: Optional[str] = Field(None, description="How to block/report")

class Advice(BaseModel):
    explanation: Explanation
    action_plan: ActionPlan

class ScamAnalysisResult(BaseModel):
    profile: UserProfile
    scout_report: ScoutReport
    explanation: Explanation
    action_plan: ActionPlan
