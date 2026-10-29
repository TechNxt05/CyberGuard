import os
import sys
import pytest


from app.services.entity_resolution_service import entity_resolver
from app.services.campaign_service import campaign_service

def test_entity_normalization():
    eid_1, val_1 = entity_resolver.normalize("Phone", "+91 98765 43210")
    eid_2, val_2 = entity_resolver.normalize("Phone", "9876543210")
    assert eid_1 == eid_2
    assert val_1 == "+919876543210"

    upi_id, upi_val = entity_resolver.normalize("UPI", "Pay.Refund8821@YBL")
    assert upi_id == "upi_pay.refund8821@ybl"
    assert upi_val == "pay.refund8821@ybl"

def test_entity_link_confidence():
    ent_a = {"entity_id": "phone_+919876543210"}
    ent_b = {"entity_id": "upi_pay.refund8821@ybl"}
    link = entity_resolver.compute_link_confidence(ent_a, ent_b, ["same_wallet", "same_upi", "used_in_same_case"])
    assert link["confidence"] >= 0.90
    assert link["status"] == "CONFIRMED_BY_EVIDENCE"

def test_campaign_detection():
    cases = [
        {"case_id": "case_001", "entities": [{"entity_id": "upi_scammer@ybl"}]},
        {"case_id": "case_002", "entities": [{"entity_id": "upi_scammer@ybl"}]}
    ]
    clusters = campaign_service.detect_campaigns(cases)
    assert len(clusters) == 1
    assert clusters[0]["case_count"] == 2
    assert clusters[0]["primary_indicator"] == "upi_scammer@ybl"

if __name__ == "__main__":
    test_entity_normalization()
    test_entity_link_confidence()
    test_campaign_detection()
    print("ALL PHASE C TESTS PASSED SUCCESSFULLY!")
