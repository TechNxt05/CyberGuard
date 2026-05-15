from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from backend.app.schemas.resolution import IncidentRequest, CaseState, IncidentDimensions, ResolutionStrategy, AuthorityContact
from backend.app.agents.resolution.incident_understanding import understand_incident
from backend.app.agents.resolution.strategy_agent import create_strategy
from backend.app.agents.resolution.authority_agent import map_authorities
from backend.app.agents.resolution.assistants import guide_step
from backend.app.agents.resolution.state_agent import save_case_state
from backend.app.agents.resolution.research_agent import search_incident_info
import uuid

from backend.app.services.investigation_engine import InvestigationEngine

class ResolutionState(TypedDict):
    request: IncidentRequest
    case_state: CaseState | None
    current_guide: str | None
    research_findings: str | None
    investigation_insights: List[str] | None

def understanding_node(state: ResolutionState):
    request = state['request']
    dimensions = understand_incident(request.description, request.user_context)
    
    case_state = CaseState(
        incident_id=str(uuid.uuid4()),
        dimensions=dimensions,
        strategy=ResolutionStrategy(lifecycle_plan=[], estimated_timeline="Calculating..."),
        authorities=[]
    )
    return {"case_state": case_state}

def evidence_node(state: ResolutionState):
    case = state['case_state']
    engine = InvestigationEngine()
    case = engine.build_initial_graph(case)
    case = engine.build_initial_timeline(case)
    return {"case_state": case}

def threat_intel_node(state: ResolutionState):
    case = state['case_state']
    engine = InvestigationEngine()
    case = engine.calculate_confidence(case)
    query = f"{case.dimensions.attack_type} {case.dimensions.summary}"
    findings = search_incident_info(query, state['request'].user_context)
    return {"research_findings": findings}

def strategy_node(state: ResolutionState):
    case = state['case_state']
    research = state.get('research_findings', "")
    strategy = create_strategy(case.dimensions, research_context=research)
    case.strategy = strategy
    return {"case_state": case}

def recovery_node(state: ResolutionState):
    case = state['case_state']
    if case.strategy.lifecycle_plan:
        first_step = case.strategy.lifecycle_plan[0]
        guide = guide_step(first_step)
        return {"current_guide": guide}
    return {"current_guide": "No steps generated."}

def authority_node(state: ResolutionState):
    case = state['case_state']
    authorities = map_authorities(case.dimensions, state['request'].user_context)
    case.authorities = authorities
    case.status = "in_progress"
    return {"case_state": case}

def prevention_node(state: ResolutionState):
    # Simulates prevention steps generation
    case = state['case_state']
    return {"investigation_insights": ["Prevention measures generated based on threat intel."]}

def save_node(state: ResolutionState):
    case = state['case_state']
    save_case_state(case)
    return {"case_state": case}

workflow = StateGraph(ResolutionState)

workflow.add_node("understanding", understanding_node)
workflow.add_node("evidence", evidence_node)
workflow.add_node("threat_intel", threat_intel_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("recovery", recovery_node)
workflow.add_node("authority_mapper", authority_node)
workflow.add_node("prevention", prevention_node)
workflow.add_node("save", save_node)

workflow.set_entry_point("understanding")

# Parallel Execution
workflow.add_edge("understanding", "evidence")
workflow.add_edge("understanding", "threat_intel")

workflow.add_edge("evidence", "strategy")
workflow.add_edge("threat_intel", "strategy")

workflow.add_edge("strategy", "recovery")
workflow.add_edge("strategy", "authority_mapper")
workflow.add_edge("strategy", "prevention")

workflow.add_edge("recovery", "save")
workflow.add_edge("authority_mapper", "save")
workflow.add_edge("prevention", "save")
workflow.add_edge("save", END)

cyber_resolve_app = workflow.compile()
