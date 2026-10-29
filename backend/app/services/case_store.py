"""MongoDB persistence for user cases, chat history, tasks and analysed scam reports."""
import uuid
from datetime import datetime

from fastapi import HTTPException

from app.db.mongodb import get_db
from app.schemas.case import Case, CaseMessage, Task
from app.schemas.common import ScamAnalysisResult

CASE_DETAIL_FIELDS = {"incident_summary", "attack_type", "incident_logic", "prevention_tips", "title", "current_phase"}


async def _db():
    db = await get_db()
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured.")
    return db


async def ensure_indexes() -> None:
    db = await _db()
    await db["cases"].create_index([("user_id", 1), ("updated_at", -1)])
    await db["case_messages"].create_index([("case_id", 1), ("user_id", 1), ("timestamp", -1)])
    await db["case_tasks"].create_index([("case_id", 1), ("user_id", 1)], unique=True)
    await db["case_state"].create_index([("case_id", 1), ("user_id", 1)], unique=True)
    await db["scam_reports"].create_index([("timestamp", -1)])


async def create_case(user_id: str, title: str, summary: str = "") -> str:
    db = await _db()
    case_id = str(uuid.uuid4())
    new_case = Case(_id=case_id, user_id=user_id, title=title, incident_summary=summary).model_dump(by_alias=True)
    await db["cases"].insert_one(new_case)
    await db["case_state"].insert_one({"case_id": case_id, "user_id": user_id, "data": {}})
    return case_id


async def get_case(user_id: str, case_id: str) -> dict | None:
    db = await _db()
    return await db["cases"].find_one({"_id": case_id, "user_id": user_id})


async def list_user_cases(user_id: str) -> list[dict]:
    db = await _db()
    return await db["cases"].find({"user_id": user_id}).sort("updated_at", -1).to_list(length=50)


async def add_case_message(case_id: str, user_id: str, sender: str, content: str) -> None:
    db = await _db()
    msg = CaseMessage(case_id=case_id, user_id=user_id, sender=sender, content=content).model_dump()
    await db["case_messages"].insert_one(msg)


async def get_case_history(case_id: str, user_id: str, limit: int = 50) -> list[dict]:
    db = await _db()
    cursor = db["case_messages"].find({"case_id": case_id, "user_id": user_id}, {"_id": 0}).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    return msgs[::-1]  # chronological order


async def update_case_state(case_id: str, user_id: str, state_data: dict) -> None:
    db = await _db()
    await db["case_state"].update_one(
        {"case_id": case_id, "user_id": user_id},
        {"$set": {"data": state_data, "updated_at": datetime.utcnow()}},
        upsert=True,
    )


async def get_case_state(case_id: str, user_id: str) -> dict:
    db = await _db()
    state_doc = await db["case_state"].find_one({"case_id": case_id, "user_id": user_id})
    return state_doc.get("data", {}) if state_doc else {}


async def update_case_details(case_id: str, user_id: str, updates: dict) -> None:
    safe_updates = {k: v for k, v in updates.items() if k in CASE_DETAIL_FIELDS}
    if not safe_updates:
        return
    db = await _db()
    safe_updates["updated_at"] = datetime.utcnow()
    await db["cases"].update_one({"_id": case_id, "user_id": user_id}, {"$set": safe_updates})


async def add_tasks(case_id: str, user_id: str, tasks: list[Task]) -> None:
    if not tasks:
        return
    db = await _db()
    await db["case_tasks"].update_one(
        {"case_id": case_id, "user_id": user_id},
        {"$push": {"tasks": {"$each": [t.model_dump() for t in tasks]}}},
        upsert=True,
    )


async def update_task_status(case_id: str, user_id: str, task_id: str, status: str) -> bool:
    db = await _db()
    result = await db["case_tasks"].update_one(
        {"case_id": case_id, "user_id": user_id, "tasks.task_id": task_id},
        {"$set": {"tasks.$.status": status}},
    )
    return result.matched_count > 0


async def get_tasks(case_id: str, user_id: str) -> list[dict]:
    db = await _db()
    doc = await db["case_tasks"].find_one({"case_id": case_id, "user_id": user_id})
    return doc.get("tasks", []) if doc else []


async def store_scam_case(result: ScamAnalysisResult) -> None:
    db = await _db()
    data = result.model_dump()
    data["timestamp"] = datetime.utcnow()
    await db["scam_reports"].insert_one(data)
