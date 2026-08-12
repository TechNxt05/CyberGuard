import re
from typing import List, Dict, Any, Optional

SUPPORTED_ENTITY_TYPES = [
    "Person", "Phone", "Email", "UPI", "Bank Account", "Wallet",
    "URL", "Domain", "IP", "Device", "Transaction", "Merchant",
    "Organization", "Platform", "Case", "Evidence", "Event", "Campaign"
]

class EntityResolutionService:
    """
    Entity Resolution & Linking Service.
    Applies canonical normalization across 18 entity types and computes confidence-scored links
    with evidence provenance.
    """

    def normalize(self, entity_type: str, raw_value: str) -> tuple[str, str]:
        """
        Returns (canonical_entity_id, canonical_value).
        """
        val = str(raw_value).strip()
        etype_upper = entity_type.upper().strip()

        if etype_upper == "PHONE":
            # Canonical Indian 10-digit phone format: +91XXXXXXXXXX
            digits = re.sub(r'\D', '', val)
            if len(digits) == 10:
                digits = "91" + digits
            elif len(digits) == 12 and digits.startswith("91"):
                pass
            canonical = f"+{digits}" if len(digits) == 12 else val.lower()
            return f"phone_{canonical}", canonical

        elif etype_upper == "UPI":
            # Canonical UPI format: lowercase pattern@bank
            canonical = val.lower().strip()
            return f"upi_{canonical}", canonical

        elif etype_upper == "EMAIL":
            canonical = val.lower().strip()
            return f"email_{canonical}", canonical

        elif etype_upper in ["URL", "DOMAIN"]:
            canonical = val.lower().replace("https://", "").replace("http://", "").rstrip("/")
            return f"url_{canonical}", canonical

        elif etype_upper == "WALLET":
            canonical = val.strip()
            return f"wallet_{canonical}", canonical

        else:
            canonical = val.lower().strip()
            return f"{etype_upper.lower()}_{canonical}", val

    def compute_link_confidence(self, entity_a: Dict[str, Any], entity_b: Dict[str, Any], shared_signals: List[str]) -> Dict[str, Any]:
        """
        Computes link confidence based on shared infrastructure and evidence signals.
        """
        base_confidence = 0.5
        score_additions = {
            "same_wallet": 0.40,
            "same_upi": 0.35,
            "same_phone": 0.30,
            "same_url": 0.25,
            "same_campaign": 0.20,
            "used_in_same_case": 0.15
        }

        confidence = base_confidence
        for signal in shared_signals:
            confidence += score_additions.get(signal, 0.10)

        final_confidence = min(0.99, round(confidence, 2))

        return {
            "source_entity": entity_a.get("entity_id"),
            "target_entity": entity_b.get("entity_id"),
            "relationship_type": "LINKED_TO",
            "confidence": final_confidence,
            "shared_signals": shared_signals,
            "status": "CONFIRMED_BY_EVIDENCE" if final_confidence >= 0.85 else "SUSPECTED"
        }

entity_resolver = EntityResolutionService()
