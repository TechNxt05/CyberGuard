import re
from typing import List, Dict, Any
from app.schemas.evidence import EvidenceItem, EvidenceClaim, VerificationStatus

class EvidenceVerifierEngine:
    """
    Evidence Verification Engine.
    Verifies extracted claims against supporting and contradictory evidence items
    to ensure AI-derived inferences are never silently accepted as unverified facts.
    """

    def verify_claim(self, claim_text: str, primary_evidence: EvidenceItem, case_evidence_items: List[EvidenceItem]) -> EvidenceClaim:
        supporting = [primary_evidence.evidence_id]
        contradictory = []
        
        claim_lower = claim_text.lower()
        
        # Check for contradictions across all case evidence
        for item in case_evidence_items:
            if item.evidence_id == primary_evidence.evidence_id:
                continue
                
            item_text = (item.ocr_text or "").lower()
            
            # Simple conflict detection heuristic: if dates or amounts differ for same entity
            if "paid" in claim_lower or "amount" in claim_lower:
                amounts_claim = re.findall(r'\b\d{3,7}\b', claim_lower)
                amounts_item = re.findall(r'\b\d{3,7}\b', item_text)
                
                if amounts_claim and amounts_item and not set(amounts_claim).intersection(set(amounts_item)):
                    contradictory.append(item.evidence_id)
                elif amounts_claim and set(amounts_claim).intersection(set(amounts_item)):
                    supporting.append(item.evidence_id)

        if contradictory:
            status: VerificationStatus = "CONTRADICTED"
            confidence = 0.3
            notes = f"Conflict detected with evidence item(s): {', '.join(contradictory)}"
        elif len(supporting) > 1:
            status = "VERIFIED"
            confidence = 0.95
            notes = f"Verified across {len(supporting)} independent evidence sources."
        elif len(supporting) == 1 and primary_evidence.confidence >= 0.9:
            status = "PARTIALLY_VERIFIED"
            confidence = 0.75
            notes = "Single source evidence. Requires secondary confirmation."
        else:
            status = "UNVERIFIED"
            confidence = 0.4
            notes = "Insufficient corroborating evidence."

        return EvidenceClaim(
            claim_text=claim_text,
            evidence_id=primary_evidence.evidence_id,
            verification_status=status,
            supporting_evidence_ids=supporting,
            contradictory_evidence_ids=contradictory,
            confidence=confidence,
            notes=notes
        )

evidence_verifier = EvidenceVerifierEngine()
