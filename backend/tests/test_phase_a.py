import os
import sys
import pytest

# Ensure project root is in sys.path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.schemas.case import InvestigationCase, CaseStatus
from backend.app.schemas.task import InvestigationTask
from backend.app.schemas.case_revision import CaseRevision
from backend.app.workflows.planner import planner

def test_investigation_case_schema():
    case = InvestigationCase(
        title="Test Phishing Investigation",
        description="Fake SBI link received over SMS",
        case_type="phishing"
    )
    assert case.case_id is not None
    assert case.status == "CREATED"
    assert case.current_phase == "intake"
    assert case.organization_id == "default_org"

def test_investigation_planner_decomposition():
    case = InvestigationCase(
        title="UPI Fraud Case",
        description="Victim paid 5000 INR to pay.refund8821@ybl",
        case_type="upi_fraud"
    )
    tasks = planner.create_initial_plan(case, case.description)
    assert len(tasks) == 7
    assert tasks[0].agent_type == "UnderstandingAgent"
    assert tasks[1].agent_type == "EvidenceAgent"
    assert tasks[1].dependencies == [tasks[0].task_id]

def test_case_goal_revision():
    case = InvestigationCase(
        title="Initial UPI Fraud",
        description="UPI fraud report"
    )
    revision = planner.revise_investigation_goal(
        case=case,
        new_evidence_desc="Credit card statement showing Unauthorized $500 international charge",
        reason="Evidence shifted from local UPI fraud to international card compromise",
        new_hypothesis="Card Credential Theft"
    )
    assert revision.case_id == case.case_id
    assert "Revised Goal" in case.investigation_goal
    assert case.active_hypotheses[0] == "Card Credential Theft"

if __name__ == "__main__":
    test_investigation_case_schema()
    test_investigation_planner_decomposition()
    test_case_goal_revision()
    print("ALL PHASE A TESTS PASSED SUCCESSFULLY!")
