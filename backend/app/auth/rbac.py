from typing import Literal, List, Dict
from pydantic import BaseModel

Role = Literal["ADMIN", "INVESTIGATOR", "ANALYST", "REVIEWER", "AUDITOR", "VIEWER"]

ROLE_PERMISSIONS: Dict[Role, List[str]] = {
    "ADMIN": ["case:read", "case:write", "case:delete", "evidence:read", "evidence:write", "report:generate", "action:approve", "audit:read"],
    "INVESTIGATOR": ["case:read", "case:write", "evidence:read", "evidence:write", "report:generate", "action:approve"],
    "ANALYST": ["case:read", "case:write", "evidence:read", "evidence:write", "report:generate"],
    "REVIEWER": ["case:read", "evidence:read", "action:approve"],
    "AUDITOR": ["case:read", "evidence:read", "audit:read"],
    "VIEWER": ["case:read", "evidence:read"]
}

class UserContext(BaseModel):
    user_id: str
    organization_id: str = "default_org"
    role: Role = "INVESTIGATOR"

class RBACService:
    @staticmethod
    def check_permission(user_context: UserContext, required_permission: str) -> bool:
        user_perms = ROLE_PERMISSIONS.get(user_context.role, [])
        return required_permission in user_perms

rbac_service = RBACService()
