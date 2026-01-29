# form mcp.server.fastapi import FastAPIServer #(Removed due to import error)
# from mcp.types import TextContent, ImageContent, EmbeddedResource
from backend.app.schemas.case import Case, Task, CaseMessage
from backend.app.schemas.resolution import CaseState
from backend.app.db.mongodb import get_db
from datetime import datetime
import uuid

class FastAPIServer:
    def __init__(self, name):
        self.name = name
    
    def tool(self):
        def decorator(func):
            return func
        return decorator

mcp = FastAPIServer("Memory & Case Management MCP")

@mcp.tool()
async def create_case(user_id: str, title: str, summary: str = "") -> str:
    """Creates a new cyber incident case for a user. Returns the Case ID."""
    db = await get_db()
    case_id = str(uuid.uuid4())
    
    new_case = Case(
        _id=case_id,
        user_id=user_id,
        title=title,
        incident_summary=summary,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    ).model_dump(by_alias=True)
    
    await db["cases"].insert_one(new_case)
    
    # Initialize empty state
    await db["case_state"].insert_one({
        "case_id": case_id,
        "user_id": user_id,
        "data": {} # Will hold the CaseState object
    })
    
    return case_id

@mcp.tool()
async def get_case(user_id: str, case_id: str) -> dict:
    """Retrieves case details."""
    db = await get_db()
    case = await db["cases"].find_one({"_id": case_id, "user_id": user_id})
    if not case:
        return {"error": "Case not found"}
    return case

@mcp.tool()
async def list_user_cases(user_id: str) -> list[dict]:
    """Lists all active cases for a user."""
    db = await get_db()
    cursor = db["cases"].find({"user_id": user_id}).sort("updated_at", -1)
    cases = await cursor.to_list(length=50)
    for c in cases:
        c["_id"] = str(c["_id"])
    return cases

@mcp.tool()
async def add_case_message(case_id: str, user_id: str, sender: str, content: str):
    """Stores a chat message in the case history."""
    db = await get_db()
    msg = CaseMessage(
        case_id=case_id,
        user_id=user_id,
        sender=sender,
        content=content
    ).model_dump()
    await db["case_messages"].insert_one(msg)
    return "Message saved"

@mcp.tool()
async def get_case_history(case_id: str, user_id: str, limit: int = 20) -> list[dict]:
    """Retrieves recent chat history for context."""
    db = await get_db()
    cursor = db["case_messages"].find({"case_id": case_id, "user_id": user_id}).sort("timestamp", -1).limit(limit)
    msgs = await cursor.to_list(length=limit)
    for m in msgs:
        m["_id"] = str(m["_id"])
    return msgs[::-1] # Return in chronological order

@mcp.tool()
async def update_case_state(case_id: str, user_id: str, state_data: dict):
    """Updates the persistent reasoning state of the case."""
    db = await get_db()
    await db["case_state"].update_one(
        {"case_id": case_id, "user_id": user_id},
        {"$set": {"data": state_data, "updated_at": datetime.utcnow()}},
        upsert=True
    )
    return "State updated"

@mcp.tool()
async def get_case_state(case_id: str, user_id: str) -> dict:
    """Retrieves the reasoning state."""
    db = await get_db()
    state_doc = await db["case_state"].find_one({"case_id": case_id, "user_id": user_id})
    return state_doc.get("data", {}) if state_doc else {}

@mcp.tool()
async def update_case_details(case_id: str, user_id: str, updates: dict) -> str:
    """Updates case metadata (summary, attack_type, prevention_tips)."""
    db = await get_db()
    
    # Allowed keys for safety
    allowed_keys = ["incident_summary", "attack_type", "incident_logic", "prevention_tips", "title"]
    safe_updates = {k: v for k, v in updates.items() if k in allowed_keys}
    
    print(f"--- DEBUG: update_case_details called with {list(safe_updates.keys())} ---", flush=True)
    
    if safe_updates:
        safe_updates["updated_at"] = datetime.utcnow()
        # FIX: The _id is stored as a string UUID in create_case, so we MUST NOT convert it to ObjectId.
        query_id = case_id

        result = await db["cases"].update_one(
            {"_id": query_id, "user_id": user_id},
            {"$set": safe_updates}
        )
        print(f"--- DEBUG: update_case_details matched={result.matched_count} modified={result.modified_count} ---", flush=True)
        return "Case details updated"
    
    print("--- DEBUG: update_case_details - No valid updates provided ---", flush=True)
    return "No valid updates provided"

@mcp.tool()
async def add_task(case_id: str, user_id: str, label: str, description: str = "", action_link: str = None, action_type: str = None):
    """Adds a todo task to the case."""
    print(f"--- DEBUG: add_task called for case {case_id} task {label} ---", flush=True)
    db = await get_db()
    task = Task(
        label=label, 
        description=description,
        action_link=action_link, 
        action_type=action_type
    ).model_dump()
    result = await db["case_tasks"].update_one(
        {"case_id": case_id, "user_id": user_id},
        {"$push": {"tasks": task}},
        upsert=True
    )
    print(f"--- DEBUG: add_task result matched={result.matched_count} modified={result.modified_count} upserted={result.upserted_id} ---", flush=True)
    return "Task added"

@mcp.tool()
async def update_task_status(case_id: str, user_id: str, label: str, status: str):
    """Updates the status of a specific task (pending/completed)."""
    db = await get_db()
    # Find the case tasks doc
    await db["case_tasks"].update_one(
        {"case_id": case_id, "user_id": user_id, "tasks.label": label},
        {"$set": {"tasks.$.status": status}}
    )
    return f"Task '{label}' marked as {status}"

@mcp.tool()
async def get_tasks(case_id: str, user_id: str):
    """Retrieves all tasks for a case."""
    print(f"--- DEBUG: get_tasks called for case {case_id} ---", flush=True)
    db = await get_db()
    doc = await db["case_tasks"].find_one({"case_id": case_id, "user_id": user_id})
    tasks = doc.get("tasks", []) if doc else []
    print(f"--- DEBUG: get_tasks found {len(tasks)} tasks ---", flush=True)
    return tasks

# ==========================================
# LEGACY SCAMSHIELD TOOLS (Restored)
# ==========================================

from backend.app.schemas.common import ScamAnalysisResult

@mcp.tool()
async def store_scam_case(result: ScamAnalysisResult):
    """Stores a processed scam case for future learning."""
    db = await get_db()
    # Serialize Pydantic model
    data = result.model_dump()
    data["timestamp"] = datetime.utcnow()
    await db["scam_reports"].insert_one(data)
    return "Case stored in memory"

@mcp.tool()
async def retrieve_similar_cases(scam_type: str) -> list[dict]:
    """Retrieves similar past cases to improve detection."""
    db = await get_db()
    # Simple finding by scam_type (Attack Type typically) in user_profile or explanation
    # For MVP, just return last 5 reports
    cursor = db["scam_reports"].find().sort("timestamp", -1).limit(5)
    cases = await cursor.to_list(length=5)
    
    # Convert ObjectId to string for JSON serialization
    for c in cases:
        c["_id"] = str(c["_id"])
        
    return cases
