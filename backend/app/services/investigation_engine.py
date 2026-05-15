import uuid
from datetime import datetime
from typing import List, Dict, Any
from backend.app.schemas.resolution import CaseState, GraphNode, GraphEdge, TimelineEvent, ConfidenceScores

class InvestigationEngine:
    @staticmethod
    def build_initial_graph(case_state: CaseState) -> CaseState:
        """
        Constructs the investigation graph nodes and edges from incident dimensions.
        """
        nodes = []
        edges = []
        
        # Victim Node
        victim_id = "node_victim"
        nodes.append(GraphNode(id=victim_id, type="victim", label="Victim (User)").model_dump())
        
        # Attack Node
        scammer_id = "node_scammer"
        nodes.append(GraphNode(id=scammer_id, type="scammer", label=f"Attacker ({case_state.dimensions.attack_type})").model_dump())
        
        # Initial Edge
        edges.append(GraphEdge(id=str(uuid.uuid4()), source=victim_id, target=scammer_id, label="targeted_by").model_dump())
        
        # Extract Entities if any (Placeholder for real extraction)
        # In a real scenario, we'd parse entities from dimensions.summary or evidence
        
        case_state.graph_data = {"nodes": nodes, "edges": edges}
        return case_state

    @staticmethod
    def build_initial_timeline(case_state: CaseState) -> CaseState:
        """
        Creates the initial chronological events.
        """
        events = []
        
        events.append(TimelineEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            event_type="incident_start",
            description=f"Incident Reported: {case_state.dimensions.summary}",
            impact="Critical" if case_state.dimensions.urgency == "critical" else "Moderate"
        ))
        
        case_state.timeline = events
        return case_state

    @staticmethod
    def calculate_confidence(case_state: CaseState) -> CaseState:
        """
        Simulates confidence scoring based on incident patterns.
        """
        # Heuristic-based scoring (would be LLM-driven in production)
        scam_likelihood = 0.95 if "fraud" in case_state.dimensions.attack_type.lower() else 0.70
        sophistication = 0.40 if "upi" in case_state.dimensions.incident_logic.lower() else 0.80
        
        case_state.confidence_metrics = ConfidenceScores(
            scam_likelihood=scam_likelihood,
            attack_sophistication=sophistication,
            recovery_probability=0.65,
            urgency_score=0.90 if case_state.dimensions.urgency == "critical" else 0.50
        )
        return case_state
