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

class ResolutionState(TypedDict):
    request: IncidentRequest
    case_state: CaseState | None
    current_guide: str | None
    research_findings: str | None # NEW: Store research data

def understanding_node(state: ResolutionState):
    request = state['request']
    dimensions = understand_incident(request.description, request.user_context)
    
    # Initialize basic Case State
    case_state = CaseState(
        incident_id=str(uuid.uuid4()),
        dimensions=dimensions,
        strategy=ResolutionStrategy(lifecycle_plan=[], estimated_timeline="Calculated next"),
        authorities=[]
    )
    return {"case_state": case_state}

def research_node(state: ResolutionState):
    """
    Performs authentic web research based on the understanding.
    """
    case = state['case_state']
    # Formulate a search query based on attack type and summary
    query = f"{case.dimensions.attack_type} {case.dimensions.summary} remediation steps"
    
    findings = search_incident_info(query, state['request'].user_context)
    return {"research_findings": findings}

def strategy_node(state: ResolutionState):
    case = state['case_state']
    research = state.get('research_findings', "")
    
    # Pass research to strategy agent (Modify create_strategy to accept it)
    strategy = create_strategy(case.dimensions, research_context=research)
    case.strategy = strategy
    return {"case_state": case}

def authority_node(state: ResolutionState):
    case = state['case_state']
    authorities = map_authorities(case.dimensions, state['request'].user_context)
    case.authorities = authorities
    case.status = "in_progress"
    return {"case_state": case}

def guide_node(state: ResolutionState):
    case = state['case_state']
    # Generate guide for the first incomplete step
    if case.strategy.lifecycle_plan:
        first_step = case.strategy.lifecycle_plan[0]
        action_lower = first_step.action.lower()
        
        # Smart Selector for Guidance
        if "cybercrime.gov" in action_lower:
            from backend.app.agents.resolution.website_guidance_agent import get_website_guide
            guide = get_website_guide("cybercrime.gov.in")
        elif "instagram" in action_lower and "hack" in action_lower:
             from backend.app.agents.resolution.website_guidance_agent import get_website_guide
             guide = get_website_guide("Instagram Hacked Page")
        else:
            # Fallback to generic micro-guide
            guide = guide_step(first_step)
            
        return {"current_guide": guide}
    return {"current_guide": "No steps generated."}

def save_node(state: ResolutionState):
    case = state['case_state']
    save_case_state(case)
    return {"case_state": case}

workflow = StateGraph(ResolutionState)

workflow.add_node("understand", understanding_node)
workflow.add_node("research", research_node) # NEW Node
workflow.add_node("strategize", strategy_node)
workflow.add_node("map_authority", authority_node)
workflow.add_node("guide", guide_node)
workflow.add_node("save", save_node)

workflow.set_entry_point("understand")
workflow.add_edge("understand", "research") # Edge to Research
workflow.add_edge("research", "strategize") # Edge from Research
workflow.add_edge("strategize", "map_authority")
workflow.add_edge("map_authority", "guide")
workflow.add_edge("guide", "save")
workflow.add_edge("save", END)

cyber_resolve_app = workflow.compile()
