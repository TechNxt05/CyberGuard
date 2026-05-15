from pydantic import BaseModel, Field
from typing import List, Dict, Any

class PriorityAction(BaseModel):
    action: str
    deadline: str
    impact: str

class ConfidenceResponse(BaseModel):
    scamLikelihood: int
    attackSophistication: str
    sophisticationScore: int
    recoveryProbability: int
    urgencyLevel: str
    urgencyReason: str
    timeToAct: str
    priorityActions: List[PriorityAction]
    riskFactors: List[str]
    mitigatingFactors: List[str]

class ConfidenceRequest(BaseModel):
    incidentDescription: str
    extractedEntities: Dict[str, Any]
