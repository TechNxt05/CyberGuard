import os
import sys
import pytest


from app.auth.rbac import rbac_service, UserContext
from app.db.audit_log import audit_logger

def test_rbac_permissions():
    investigator = UserContext(user_id="user_inv", role="INVESTIGATOR")
    viewer = UserContext(user_id="user_view", role="VIEWER")

    assert rbac_service.check_permission(investigator, "case:write") is True
    assert rbac_service.check_permission(investigator, "action:approve") is True

    assert rbac_service.check_permission(viewer, "case:read") is True
    assert rbac_service.check_permission(viewer, "case:write") is False
    assert rbac_service.check_permission(viewer, "action:approve") is False

def test_audit_logging():
    entry = audit_logger.log_action(
        user_id="user_inv",
        action="REPORT_GENERATED",
        case_id="case_001",
        details={"report_type": "C6_PDF"}
    )
    assert entry.action == "REPORT_GENERATED"
    
    trail = audit_logger.get_audit_trail("case_001")
    assert len(trail) >= 1
    assert trail[-1].user_id == "user_inv"

if __name__ == "__main__":
    test_rbac_permissions()
    test_audit_logging()
    print("ALL PHASE H TESTS PASSED SUCCESSFULLY!")
