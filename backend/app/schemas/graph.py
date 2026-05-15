from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class GraphNode(BaseModel):
    id: str
    type: str  # e.g., 'victim', 'scammer', 'mule_account', 'url', 'ip', 'wallet'
    label: str
    metadata: Optional[Dict[str, Any]] = None

class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    label: str
    type: Optional[str] = "animated"

class GraphResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]

class GraphRequest(BaseModel):
    incidentDescription: str
    extractedEntities: Dict[str, Any]
