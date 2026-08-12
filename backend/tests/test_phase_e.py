import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.events.event_bus import event_bus, InvestigationEvent

def test_event_bus_publish_subscribe():
    received_events = []

    def handle_repeat_threat(event: InvestigationEvent):
        received_events.append(event)

    event_bus.subscribe("RepeatThreatDetected", handle_repeat_threat)

    event = InvestigationEvent(
        case_id="case_001",
        event_type="RepeatThreatDetected",
        severity="critical",
        payload={"entity_id": "upi_scammer@ybl", "occurrences": 3}
    )
    event_bus.publish(event)

    assert len(received_events) == 1
    assert received_events[0].case_id == "case_001"
    assert received_events[0].severity == "critical"

    history = event_bus.get_event_log("case_001")
    assert len(history) >= 1

if __name__ == "__main__":
    test_event_bus_publish_subscribe()
    print("ALL PHASE E TESTS PASSED SUCCESSFULLY!")
