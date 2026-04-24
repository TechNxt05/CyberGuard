from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from backend.app.auth.clerk_auth import get_current_user
from backend.app.db.mongodb import db
from backend.app.schemas.case import ScamPattern

router = APIRouter(prefix="/api/scam-patterns", tags=["Scam Patterns"])

class PatternSearchRequest(BaseModel):
    query: str
    top_k: int = 5

@router.post("/search")
async def search_pattern(request: PatternSearchRequest, user_id: str = Depends(get_current_user)):
    """Searches the Vector DB for similar scam patterns."""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    # In a real production setup, the model should be loaded once globally
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode(request.query).tolist()
    
    if db.db is None:
        raise HTTPException(status_code=500, detail="Database not connected")
        
    # MongoDB Vector Search Aggregation Pipeline
    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": request.top_k * 10,
                "limit": request.top_k
            }
        },
        {
            "$project": {
                "pattern_text": 1,
                "scam_type": 1,
                "severity": 1,
                "score": { "$meta": "vectorSearchScore" }
            }
        }
    ]
    
    try:
        cursor = db.db["scamPatterns"].aggregate(pipeline)
        results = await cursor.to_list(length=request.top_k)
        
        # Convert ObjectId
        for res in results:
            if "_id" in res:
                res["_id"] = str(res["_id"])
                
        return {"status": "success", "matches": results}
    except Exception as e:
        print(f"Vector Search Error: {e}")
        # Fallback if index is not created
        return {"status": "warning", "matches": [], "detail": "Vector index missing or search failed"}
