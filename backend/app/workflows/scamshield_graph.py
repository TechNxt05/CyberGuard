from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from backend.app.schemas.common import AnalysisRequest, UserProfile, ScoutReport, Explanation, ActionPlan, ScamAnalysisResult
from backend.app.agents.user_profiling_agent import profile_user
from backend.app.agents.scam_detection_agent import detect_scam
from backend.app.agents.explainability_agent import generate_explanation
from backend.app.agents.response_agent import generate_action_plan
from backend.app.agents.memory_agent import update_memory

from backend.app.agents.resolution.research_agent import search_incident_info # Re-use research agent

class AgentState(TypedDict):
    request: AnalysisRequest
    user_profile: UserProfile | None
    scout_report: ScoutReport | None
    research_findings: str | None # NEW: Authentic data
    explanation: Explanation | None
    action_plan: ActionPlan | None
    final_output: ScamAnalysisResult | None

def profiling_node(state: AgentState):
    # If message is empty (image only), use a placeholder for profiling or skip
    msg = state['request'].message or "Image analysis request"
    profile = profile_user(msg, state['request'].source)
    return {"user_profile": profile}

def detection_node(state: AgentState):
    report = detect_scam(
        message=state['request'].message, 
        user_profile=state['user_profile'],
        image_base64=state['request'].image_base64
    )
    return {"scout_report": report}

def research_node(state: AgentState):
    """
    Search for the detected scam pattern to validate authenticity.
    """
    report = state['scout_report']
    keywords = " ".join(report.detected_patterns)
    if not keywords:
        keywords = "suspicious message analysis"
        
    query = f"Is '{keywords}' a known scam?"
    findings = search_incident_info(query, {})
    return {"research_findings": findings}

def explanation_node(state: AgentState):
    research = state.get('research_findings', "")
    expl = generate_explanation(state['scout_report'], state['user_profile'], research_context=research)
    return {"explanation": expl}

def response_node(state: AgentState):
    plan = generate_action_plan(state['scout_report'])
    return {"action_plan": plan}

async def memory_node(state: AgentState):
    result = ScamAnalysisResult(
        profile=state['user_profile'],
        scout_report=state['scout_report'],
        explanation=state['explanation'],
        action_plan=state['action_plan']
    )
    await update_memory(result)
    return {"final_output": result}

workflow = StateGraph(AgentState)

workflow.add_node("profiler", profiling_node)
workflow.add_node("detector", detection_node)
workflow.add_node("research", research_node) # NEW
workflow.add_node("explainer", explanation_node)
workflow.add_node("responder", response_node)
workflow.add_node("memory", memory_node)

workflow.set_entry_point("profiler")
workflow.add_edge("profiler", "detector")
workflow.add_edge("detector", "research") # Edge to Research
workflow.add_edge("research", "explainer") # Edge from Research
workflow.add_edge("explainer", "responder")
workflow.add_edge("responder", "memory")
workflow.add_edge("memory", END)

scamshield_app = workflow.compile()
