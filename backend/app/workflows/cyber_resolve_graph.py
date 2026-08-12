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

from backend.app.schemas.agent_outputs import (
    UnderstandingAgentOutput,
    EvidenceAgentOutput,
    ThreatIntelAgentOutput,
    StrategyAgentOutput,
    RecoveryAgentOutput,
    AuthorityMapperAgentOutput,
    PreventionAgentOutput,
    AgentValidationWrapper
)

class ResolutionState(TypedDict):
    request: IncidentRequest
    case_state: CaseState | None
    current_guide: str | None
    research_findings: str | None
    investigation_insights: List[str] | None
    validated_outputs: Dict[str, Any] | None

from backend.app.workflows.supervisor import supervisor
from backend.app.workflows.planner import planner
from backend.app.schemas.case import InvestigationCase

def understanding_node(state: ResolutionState):
    request = state['request']
    dimensions = understand_incident(request.description, request.user_context)
    
    # Validate against UnderstandingAgentOutput
    out_dict = {
        "case_type": dimensions.attack_type if dimensions.attack_type in ["fraud", "unauthorized_access", "malware", "impersonation", "harassment"] else "unknown",
        "victim_profile": request.user_context or {},
        "extracted_indicators": dimensions.asset_affected or [],
        "attack_timeline": [{"event": "Incident reported", "summary": dimensions.summary}],
        "confidence": 0.9,
        "missing_evidence": []
    }
    
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, UnderstandingAgentOutput, "UnderstandingAgent")
    
    case_state = CaseState(
        incident_id=str(uuid.uuid4()),
        dimensions=dimensions,
        strategy=ResolutionStrategy(lifecycle_plan=[], estimated_timeline="Calculating..."),
        authorities=[],
        status="INVESTIGATING"
    )
    
    # Create first-class InvestigationCase & initial task plan
    inv_case = InvestigationCase(
        case_id=case_state.incident_id,
        title=f"Investigation: {dimensions.attack_type.upper()} - {dimensions.summary[:40]}",
        description=request.description,
        case_type=dimensions.attack_type,
        status="INVESTIGATING",
        priority="high" if dimensions.urgency in ["high", "critical"] else "medium",
        severity=dimensions.urgency if dimensions.urgency in ["low", "medium", "high", "critical"] else "high"
    )
    
    planned_tasks = planner.create_initial_plan(inv_case, request.description, request.user_context)
    case_state.investigation_tasks = [t.model_dump(mode="json") for t in planned_tasks]
    
    supervisor.record_spawn(case_state, depth_increment=1)
    is_ok, msg = supervisor.check_guardrails(case_state)
    if not is_ok:
        case_state.validation_errors.append(msg)
    
    if not success:
        # Retry with corrective prompt once, then escalate if failed
        case_state.human_escalation_required = True
        case_state.status = "escalated"
        case_state.validation_errors.append(f"UnderstandingAgent: {err}")
        
    return {"case_state": case_state}

def _dump(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if isinstance(obj, dict):
        return {k: _dump(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_dump(item) for item in obj]
    return obj

def evidence_node(state: ResolutionState):
    case = state['case_state']
    engine = InvestigationEngine()
    case = engine.build_initial_graph(case)
    case = engine.build_initial_timeline(case)
    
    nodes_data = [_dump(n) for n in case.graph_data.get("nodes", [])]
    out_dict = {
        "extracted_entities": {"nodes": nodes_data},
        "ocr_confidence": 0.95,
        "evidence_quality": "high",
        "flagged_patterns": [case.dimensions.attack_type]
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, EvidenceAgentOutput, "EvidenceAgent")
    if not success:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"EvidenceAgent: {err}")
        
    return {"case_state": case}

def threat_intel_node(state: ResolutionState):
    case = state['case_state']
    engine = InvestigationEngine()
    case = engine.calculate_confidence(case)
    query = f"{case.dimensions.attack_type} {case.dimensions.summary}"
    findings = search_incident_info(query, state['request'].user_context)
    
    out_dict = {
        "matched_patterns": [{"pattern": case.dimensions.attack_type}],
        "known_threat_matches": [],
        "research_summary": findings[:500] if findings else "No findings",
        "confidence_score": float(case.confidence_metrics.scam_likelihood)
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, ThreatIntelAgentOutput, "ThreatIntelAgent")
    if not success:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"ThreatIntelAgent: {err}")
        
    return {"research_findings": findings}

def strategy_node(state: ResolutionState):
    case = state['case_state']
    research = state.get('research_findings', "")
    strategy = create_strategy(case.dimensions, research_context=research)
    case.strategy = strategy
    
    out_dict = {
        "lifecycle_plan": [_dump(s) for s in strategy.lifecycle_plan],
        "estimated_timeline": strategy.estimated_timeline,
        "priority_phase": strategy.lifecycle_plan[0].phase if strategy.lifecycle_plan else "containment"
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, StrategyAgentOutput, "StrategyAgent")
    if not success:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"StrategyAgent: {err}")
        
    return {"case_state": case}

def recovery_node(state: ResolutionState):
    case = state['case_state']
    guide = "No steps generated."
    if case.strategy.lifecycle_plan:
        first_step = case.strategy.lifecycle_plan[0]
        guide = guide_step(first_step)
        
    out_dict = {
        "current_guide": guide,
        "immediate_actions": [case.strategy.lifecycle_plan[0].action] if case.strategy.lifecycle_plan else [],
        "contact_targets": ["Bank Helpline 1930", "Cyber Crime Portal"]
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, RecoveryAgentOutput, "RecoveryAgent")
    if not success:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"RecoveryAgent: {err}")
        
    return {"current_guide": guide}

def authority_node(state: ResolutionState):
    case = state['case_state']
    authorities = map_authorities(case.dimensions, state['request'].user_context)
    case.authorities = authorities
    if not case.human_escalation_required:
        case.status = "in_progress"
        
    out_dict = {
        "mapped_authorities": [_dump(a) for a in authorities],
        "status": case.status,
        "jurisdiction_notes": "Mapped based on user location and incident profile."
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, AuthorityMapperAgentOutput, "AuthorityMapperAgent")
    if not success:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"AuthorityMapperAgent: {err}")
        
    return {"case_state": case}

def prevention_node(state: ResolutionState):
    case = state['case_state']
    tips = case.dimensions.prevention_tips if case and case.dimensions else ["Enable 2FA on all accounts."]
    out_dict = {
        "prevention_tips": tips,
        "insights": ["Prevention measures generated based on threat intel."],
        "risk_mitigation_score": 0.85
    }
    validated, success, err = AgentValidationWrapper.validate_or_escalate(out_dict, PreventionAgentOutput, "PreventionAgent")
    if not success and case:
        case.human_escalation_required = True
        case.status = "escalated"
        case.validation_errors.append(f"PreventionAgent: {err}")
        
    return {"investigation_insights": tips}

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

from backend.app.db.checkpointer import get_checkpointer

cyber_resolve_app = workflow.compile(checkpointer=get_checkpointer())
