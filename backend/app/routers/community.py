"""
Community indicator reports with moderation.

Signed-in users submit a scam phone number / UPI ID / link / email / wallet. Reports stay `pending` until an
admin (Clerk user ids in ADMIN_USER_IDS) approves them; only approved reports reach threat memory, where the
"confirmed after 3 independent reporters" rule still applies.
"""
import os
import uuid
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.auth.clerk_auth import get_current_user
from app.db.mongodb import get_db
from app.services import case_store
from app.services.entity_extraction import extract_entities
from app.services.memory_service import ThreatMemoryService
from app.services.rate_limit import rate_limit, read_only

router = APIRouter(tags=["Community reports"])

report_limit = rate_limit("community_report", limit=10, window_seconds=3600)

EntityType = Literal["upi_id", "phone_number", "url", "email", "wallet_address"]


def _admins() -> set[str]:
    return {u.strip() for u in os.getenv("ADMIN_USER_IDS", "").split(",") if u.strip()}


def require_admin(user_id: str = Depends(get_current_user)) -> str:
    if user_id not in _admins():
        raise HTTPException(status_code=403, detail="Admins only")
    return user_id


async def _reports(db):
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured.")
    return db["indicator_reports"]


class IndicatorReport(BaseModel):
    entity_type: EntityType
    value: str = Field(..., min_length=3, max_length=300)
    crime_type: str = Field("unspecified", max_length=60)
    description: str = Field("", max_length=1000)


class Decision(BaseModel):
    note: str = Field("", max_length=500)


@router.get("/me/role", dependencies=[Depends(read_only)])
async def my_role(user_id: str = Depends(get_current_user)):
    return {"is_admin": user_id in _admins()}


@router.post("/api/community/reports", dependencies=[Depends(report_limit)])
async def submit_report(req: IndicatorReport, user_id: str = Depends(get_current_user), db=Depends(get_db)):
    # The value must actually look like the claimed type (regex, not LLM), so junk can't enter the queue.
    found = extract_entities(req.value).get(req.entity_type, [])
    if not found:
        raise HTTPException(status_code=422, detail=f"That doesn't look like a valid {req.entity_type.replace('_', ' ')}.")
    value = found[0]
    col = await _reports(db)
    if await col.find_one({"reporter_id": user_id, "entity_type": req.entity_type, "value": value.lower()}):
        raise HTTPException(status_code=409, detail="You have already reported this.")
    report_id = str(uuid.uuid4())
    await col.insert_one({
        "_id": report_id, "reporter_id": user_id, "entity_type": req.entity_type, "value": value.lower(),
        "crime_type": req.crime_type, "description": req.description, "status": "pending", "created_at": datetime.utcnow(),
    })
    return {"id": report_id, "status": "pending"}


@router.get("/api/community/reports/mine", dependencies=[Depends(read_only)])
async def my_reports(user_id: str = Depends(get_current_user), db=Depends(get_db)):
    col = await _reports(db)
    return await col.find({"reporter_id": user_id}, {"reporter_id": 0}).sort("created_at", -1).to_list(length=100)


@router.get("/api/admin/reports", dependencies=[Depends(read_only)])
async def pending_reports(status: Literal["pending", "approved", "rejected"] = "pending", _: str = Depends(require_admin), db=Depends(get_db)):
    col = await _reports(db)
    # Reporter ids are not exposed to moderators.
    return await col.find({"status": status}, {"reporter_id": 0}).sort("created_at", 1).to_list(length=200)


async def _decide(report_id: str, status: str, note: str, admin_id: str, db) -> dict:
    col = await _reports(db)
    report = await col.find_one({"_id": report_id, "status": "pending"})
    if not report:
        raise HTTPException(status_code=404, detail="Pending report not found")
    await col.update_one({"_id": report_id}, {"$set": {"status": status, "moderator_note": note, "reviewed_at": datetime.utcnow()}})
    await case_store.audit(f"community_report_{status}", admin_id, {"report_id": report_id})
    return report


@router.post("/api/admin/reports/{report_id}/approve", dependencies=[Depends(read_only)])
async def approve(report_id: str, decision: Decision, admin_id: str = Depends(require_admin), db=Depends(get_db)):
    report = await _decide(report_id, "approved", decision.note, admin_id, db)
    await ThreatMemoryService(db).store_entities(
        {report["entity_type"]: [report["value"]]},
        case_id=f"community:{report_id}",
        crime_type=report["crime_type"],
        reporter_id=report["reporter_id"],
    )
    return {"status": "approved"}


@router.post("/api/admin/reports/{report_id}/reject", dependencies=[Depends(read_only)])
async def reject(report_id: str, decision: Decision, admin_id: str = Depends(require_admin), db=Depends(get_db)):
    await _decide(report_id, "rejected", decision.note, admin_id, db)
    return {"status": "rejected"}
