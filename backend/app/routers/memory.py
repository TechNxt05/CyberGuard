from fastapi import APIRouter, Depends
from backend.app.services.memory_service import ThreatMemoryService
from backend.app.db.mongodb import get_db

router = APIRouter(prefix="/api/memory", tags=["memory"])

@router.get("/stats")
async def get_memory_stats(db=Depends(get_db)):
    """Dashboard stats — total tracked entities, confirmed threats."""
    service = ThreatMemoryService(db)
    return await service.get_threat_stats()

@router.get("/recent-threats")
async def get_recent_threats(limit: int = 20, db=Depends(get_db)):
    """Recent repeat-offender entities for the intelligence feed."""
    service = ThreatMemoryService(db)
    return await service.get_recent_threats(limit)

@router.post("/check")
async def check_entities(entities: dict, db=Depends(get_db)):
    """
    Check if specific entities are in the threat memory.
    Used by frontend to show threat history on entity hover.
    """
    service = ThreatMemoryService(db)
    return await service.check_entities(entities)
