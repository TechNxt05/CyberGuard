import uuid
from datetime import datetime

from app.schemas.resolution import CaseState, GraphEdge, GraphNode, TimelineEvent
from app.services.entity_extraction import extract_entities

# entity_type -> (graph node type, edge label from the attacker to the entity)
_ENTITY_NODES = {
    "upi_id": ("wallet", "receives_funds_via"),
    "wallet_address": ("wallet", "receives_funds_via"),
    "phone_number": ("phone", "contacted_via"),
    "email": ("email", "contacted_via"),
    "url": ("url", "operates"),
}


class InvestigationEngine:
    @staticmethod
    def build_initial_graph(case_state: CaseState, description: str) -> CaseState:
        """Victim -> attacker, plus every indicator actually found in the user's description."""
        victim_id, scammer_id = "node_victim", "node_scammer"
        nodes = [
            GraphNode(id=victim_id, type="victim", label="Victim (User)").model_dump(),
            GraphNode(id=scammer_id, type="scammer", label=f"Attacker ({case_state.dimensions.attack_type})").model_dump(),
        ]
        edges = [GraphEdge(id=str(uuid.uuid4()), source=victim_id, target=scammer_id, label="targeted_by").model_dump()]

        for entity_type, values in extract_entities(description).items():
            node_type, edge_label = _ENTITY_NODES[entity_type]
            for value in values:
                node_id = f"node_{entity_type}_{value}"
                nodes.append(GraphNode(id=node_id, type=node_type, label=value, metadata={"entity_type": entity_type}).model_dump())
                edges.append(GraphEdge(id=str(uuid.uuid4()), source=scammer_id, target=node_id, label=edge_label).model_dump())

        case_state.graph_data = {"nodes": nodes, "edges": edges}
        return case_state

    @staticmethod
    def build_initial_timeline(case_state: CaseState) -> CaseState:
        case_state.timeline = [TimelineEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow().isoformat(),
            event_type="incident_start",
            description=f"Incident reported: {case_state.dimensions.summary}",
            impact="Critical" if case_state.dimensions.urgency == "critical" else "Moderate",
        )]
        return case_state
