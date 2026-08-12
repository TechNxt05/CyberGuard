import os
import sys
import pytest

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.app.schemas.recovery import RecoveryAction
from backend.app.services.report_generator import report_generator

def test_recovery_action_human_approval_gate():
    action = RecoveryAction(
        case_id="case_001",
        action_type="bank_freeze",
        title="Freeze HDFC Account Collect Request",
        description="Notify bank to freeze suspicious collect request"
    )
    assert action.approval_status == "PROPOSED"

    # Execution without approval must raise ValueError
    with pytest.raises(ValueError):
        action.execute()

    # Human approves
    action.approve(user_id="investigator_john")
    assert action.approval_status == "APPROVED"
    assert action.approved_by == "investigator_john"

    # Execution works after approval
    action.execute()
    assert action.approval_status == "EXECUTED"
    assert action.completed_at is not None

def test_c6_legal_evidence_package_generation():
    pkg = report_generator.generate_package("case_001", {"attack_type": "upi_fraud", "description": "Fake UPI collect"})
    assert pkg.package_id is not None
    assert pkg.digital_signature != ""
    assert len(pkg.evidence_manifest) == 1

    json_str = report_generator.export_to_json(pkg)
    html_str = report_generator.export_to_html(pkg)

    assert "CyberGuardAI Legal Evidence Package" in html_str
    assert pkg.digital_signature in html_str

if __name__ == "__main__":
    test_recovery_action_human_approval_gate()
    test_c6_legal_evidence_package_generation()
    print("ALL PHASE G TESTS PASSED SUCCESSFULLY!")
