import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.workflows.agent_policy import policy_engine

def test_duplicate_action_caching():
    is_dup, val = policy_engine.check_duplicate_action("ThreatIntelAgent", "search_duckduckgo", "query_upi_123")
    assert is_dup is False
    assert val is None

    policy_engine.record_action("ThreatIntelAgent", "search_duckduckgo", "query_upi_123", {"status": "found_threat"})

    is_dup_2, val_2 = policy_engine.check_duplicate_action("ThreatIntelAgent", "search_duckduckgo", "query_upi_123")
    assert is_dup_2 is True
    assert val_2["status"] == "found_threat"

def test_investigation_drift_detection():
    expected = ["Understand Report", "Extract Entities", "OSINT Search"]
    actual_aligned = ["Understand Report", "Extract Entities", "OSINT Search"]
    actual_drifted = ["Irrelevant Web Scraping", "Random Query", "Unrelated Task"]

    drift_low = policy_engine.detect_investigation_drift(expected, actual_aligned)
    drift_high = policy_engine.detect_investigation_drift(expected, actual_drifted)

    assert drift_low == 0.0
    assert drift_high == 1.0

if __name__ == "__main__":
    test_duplicate_action_caching()
    test_investigation_drift_detection()
    print("ALL PHASE F TESTS PASSED SUCCESSFULLY!")
