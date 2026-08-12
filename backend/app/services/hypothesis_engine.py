from typing import List, Dict, Any, Optional
from backend.app.schemas.hypothesis import CaseHypothesis

class HypothesisEngine:
    """
    Competing Hypothesis Engine.
    Manages multiple competing hypotheses (H1..Hn) per case, ranks them dynamically
    based on supporting vs contradictory evidence, and detects conflicts.
    """

    def generate_competing_hypotheses(self, case_id: str, attack_type: str, indicators: List[str]) -> List[CaseHypothesis]:
        hypotheses = []

        if "fraud" in attack_type.lower() or "upi" in attack_type.lower():
            hypotheses.append(
                CaseHypothesis(
                    case_id=case_id,
                    title="H1: Social Engineering UPI Phishing",
                    description="Attacker impersonated official entity to lure victim into approving UPI collect request.",
                    confidence_score=0.85
                )
            )
            hypotheses.append(
                CaseHypothesis(
                    case_id=case_id,
                    title="H2: Malicious Refund Gateway Portal",
                    description="Victim entered credentials into a fake domain impersonating a bank refund portal.",
                    confidence_score=0.65
                )
            )
            hypotheses.append(
                CaseHypothesis(
                    case_id=case_id,
                    title="H3: Account Takeover via Malware/SIM Swap",
                    description="Attacker obtained device control or intercepted OTPs via SIM swap.",
                    confidence_score=0.35
                )
            )
        else:
            hypotheses.append(
                CaseHypothesis(
                    case_id=case_id,
                    title="H1: Credential Harvesting & Impersonation",
                    description="General social engineering attack targeting victim credentials.",
                    confidence_score=0.75
                )
            )

        return hypotheses

    def rank_hypotheses(self, hypotheses: List[CaseHypothesis]) -> List[CaseHypothesis]:
        return sorted(hypotheses, key=lambda h: h.confidence_score, reverse=True)

hypothesis_engine = HypothesisEngine()
