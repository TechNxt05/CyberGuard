from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.db.mongodb import get_db
from app.services.memory_service import ThreatMemoryService
from app.services.rate_limit import read_only

router = APIRouter(prefix="/api/memory", tags=["memory"], dependencies=[Depends(read_only)])


def _service(db) -> ThreatMemoryService:
    if db is None:
        raise HTTPException(status_code=503, detail="Database is not configured.")
    return ThreatMemoryService(db)


class EntityCheckRequest(BaseModel):
    entities: dict[str, list[str]] = Field(..., description="{entity_type: [values]}")


@router.get("/stats")
async def get_memory_stats(db=Depends(get_db)):
    """Totals for the dashboard: tracked indicators, confirmed threats."""
    return await _service(db).get_threat_stats()


@router.get("/recent-threats")
async def get_recent_threats(limit: int = Query(20, ge=1, le=50), db=Depends(get_db)):
    """Indicators reported in more than one investigation, most recent first."""
    return await _service(db).get_recent_threats(limit)


@router.post("/check")
async def check_entities(req: EntityCheckRequest, db=Depends(get_db)):
    """Read-only lookup: are any of these indicators already known?"""
    entities = {k: v[:20] for k, v in list(req.entities.items())[:10]}
    return await _service(db).check_entities(entities)
