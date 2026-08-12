import os
import sys
import pytest

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.schemas.evidence import EvidenceItem, EvidenceProvenanceRecord, EvidenceClaim
from backend.app.services.evidence_verifier import evidence_verifier

def test_evidence_item_hashing_and_provenance():
    raw_content = b"Fake Bank Statement Screenshot Binary Data"
    file_hash = EvidenceItem.compute_sha256(raw_content)
    
    item = EvidenceItem(
        case_id="case_test_001",
        type="bank_statement",
        source="user_upload",
        original_hash=file_hash,
        current_hash=file_hash,
        mime_type="image/png",
        ocr_text="Payment of 10000 INR to pay.refund8821@ybl at 10:30 AM"
    )
    
    item.provenance_chain.append(
        EvidenceProvenanceRecord(
            action="uploaded",
            notes="Uploaded via Mission Control Console"
        )
    )
    item.provenance_chain.append(
        EvidenceProvenanceRecord(
            action="OCR_processed",
            notes="Vision Engine extracted 10000 INR UPI transaction"
        )
    )
    
    assert item.original_hash == file_hash
    assert len(item.provenance_chain) == 2
    assert item.provenance_chain[1].action == "OCR_processed"

def test_evidence_verification_engine():
    item1 = EvidenceItem(
        case_id="case_test_001",
        type="bank_statement",
        source="upload_1",
        original_hash="hash1",
        current_hash="hash1",
        ocr_text="Transaction paid 10000 INR to scammer"
    )
    item2 = EvidenceItem(
        case_id="case_test_001",
        type="chat_export",
        source="upload_2",
        original_hash="hash2",
        current_hash="hash2",
        ocr_text="Scammer demanded 10000 INR on WhatsApp"
    )
    
    claim = evidence_verifier.verify_claim(
        claim_text="User paid 10000 INR to fraudster",
        primary_evidence=item1,
        case_evidence_items=[item1, item2]
    )
    
    assert claim.verification_status == "VERIFIED"
    assert claim.confidence >= 0.9

if __name__ == "__main__":
    test_evidence_item_hashing_and_provenance()
    test_evidence_verification_engine()
    print("ALL PHASE B TESTS PASSED SUCCESSFULLY!")
