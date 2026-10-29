"""
CyberResolve workflow: understand -> (evidence || research) -> strategy -> (guide || authorities || prevention).

Compiled without a checkpointer: each run is a single request whose result the caller persists in MongoDB.
(A checkpointer requires a thread_id on every invoke and, as MemorySaver, grows RAM forever on a 512 MB instance.)
"""
import uuid
from typing import List, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.resolution.assistants import guide_step
from app.agents.resolution.authority_agent import map_authorities
from app.agents.resolution.incident_understanding import understand_incident
from app.agents.resolution.research_agent import search_incident_info
from app.agents.resolution.strategy_agent import create_strategy
from app.schemas.case import InvestigationCase
from app.schemas.resolution import CaseState, IncidentRequest, ResolutionStrategy
from app.services.investigation_engine import InvestigationEngine
from app.workflows.planner import planner


class ResolutionState(TypedDict):
    request: IncidentRequest
    case_state: CaseState | None
    current_guide: str | None
    research_findings: str | None
    investigation_insights: List[str] | None


def understanding_node(state: ResolutionState):
    request = state["request"]
    dimensions = understand_incident(request.description, request.user_context)

    case_state = CaseState(
        incident_id=str(uuid.uuid4()),
        dimensions=dimensions,
        strategy=ResolutionStrategy(lifecycle_plan=[], estimated_timeline="Calculating..."),
        authorities=[],
        status="INVESTIGATING",
    )
    if dimensions.attack_type == "unknown":
        case_state.human_escalation_required = True

    inv_case = InvestigationCase(
        case_id=case_state.incident_id,
        title=f"Investigation: {dimensions.attack_type.upper()} - {dimensions.summary[:40]}",
        description=request.description,
        case_type=dimensions.attack_type,
        status="INVESTIGATING",
        priority="high" if dimensions.urgency in ["high", "critical"] else "medium",
        severity=dimensions.urgency if dimensions.urgency in ["low", "medium", "high", "critical"] else "high",
    )
    planned_tasks = planner.create_initial_plan(inv_case, request.description, request.user_context)
    case_state.investigation_tasks = [t.model_dump(mode="json") for t in planned_tasks]
    return {"case_state": case_state}


def evidence_node(state: ResolutionState):
    # Only this node writes case_state in its superstep (research runs in parallel and returns findings only).
    case = InvestigationEngine.build_initial_graph(state["case_state"], state["request"].description)
    case = InvestigationEngine.build_initial_timeline(case)
    return {"case_state": case}


def research_node(state: ResolutionState):
    dims = state["case_state"].dimensions
    return {"research_findings": search_incident_info(f"{dims.attack_type} {dims.summary}")}


def strategy_node(state: ResolutionState):
    case = state["case_state"]
    case.strategy = create_strategy(case.dimensions, research_context=state.get("research_findings") or "")
    return {"case_state": case}


def recovery_node(state: ResolutionState):
    plan = state["case_state"].strategy.lifecycle_plan
    return {"current_guide": guide_step(plan[0]) if plan else None}


def authority_node(state: ResolutionState):
    case = state["case_state"]
    case.authorities = map_authorities(case.dimensions, state["request"].user_context)
    case.status = "escalated" if case.human_escalation_required else "in_progress"
    return {"case_state": case}


def prevention_node(state: ResolutionState):
    return {"investigation_insights": state["case_state"].dimensions.prevention_tips}


workflow = StateGraph(ResolutionState)
workflow.add_node("understanding", understanding_node)
workflow.add_node("evidence", evidence_node)
workflow.add_node("research", research_node)
workflow.add_node("strategy", strategy_node)
workflow.add_node("recovery", recovery_node)
workflow.add_node("authority_mapper", authority_node)
workflow.add_node("prevention", prevention_node)

workflow.set_entry_point("understanding")
workflow.add_edge("understanding", "evidence")
workflow.add_edge("understanding", "research")
workflow.add_edge("evidence", "strategy")
workflow.add_edge("research", "strategy")
workflow.add_edge("strategy", "recovery")
workflow.add_edge("strategy", "authority_mapper")
workflow.add_edge("strategy", "prevention")
workflow.add_edge("recovery", END)
workflow.add_edge("authority_mapper", END)
workflow.add_edge("prevention", END)

cyber_resolve_app = workflow.compile()


async def run_resolution(request: IncidentRequest) -> tuple[CaseState, str | None]:
    result = await cyber_resolve_app.ainvoke({"request": request, "case_state": None, "current_guide": None})
    return result["case_state"], result.get("current_guide")
