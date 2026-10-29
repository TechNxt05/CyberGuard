from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.agents.explainability_agent import generate_advice
from app.agents.memory_agent import update_memory
from app.agents.resolution.research_agent import search_incident_info
from app.agents.scam_detection_agent import detect_scam
from app.agents.user_profiling_agent import profile_user
from app.schemas.common import Advice, AnalysisRequest, ScamAnalysisResult, ScoutReport, UserProfile


class AgentState(TypedDict):
    request: AnalysisRequest
    user_profile: UserProfile | None
    scout_report: ScoutReport | None
    research_findings: str | None
    advice: Advice | None
    final_output: ScamAnalysisResult | None


def profiling_node(state: AgentState):
    msg = state["request"].message or "Image analysis request"
    return {"user_profile": profile_user(msg, state["request"].source)}


def detection_node(state: AgentState):
    request = state["request"]
    report = detect_scam(
        message=request.message,
        user_profile=state["user_profile"],
        image_base64=request.image_base64,
        image_mime_type=request.image_mime_type or "image/jpeg",
    )
    return {"scout_report": report}


def research_node(state: AgentState):
    """Look the detected pattern up on the open web so the explanation can cite real reports."""
    report = state["scout_report"]
    if report.analysis_status == "failed" or not report.detected_patterns:
        return {"research_findings": ""}
    return {"research_findings": search_incident_info(" ".join(report.detected_patterns[:3]))}


def advice_node(state: AgentState):
    return {"advice": generate_advice(state["scout_report"], state["user_profile"], research_context=state.get("research_findings") or "")}


async def memory_node(state: AgentState):
    advice = state["advice"]
    result = ScamAnalysisResult(
        profile=state["user_profile"],
        scout_report=state["scout_report"],
        explanation=advice.explanation,
        action_plan=advice.action_plan,
    )
    if result.scout_report.analysis_status == "ok":
        await update_memory(result)
    return {"final_output": result}


workflow = StateGraph(AgentState)
workflow.add_node("profiler", profiling_node)
workflow.add_node("detector", detection_node)
workflow.add_node("research", research_node)
workflow.add_node("advisor", advice_node)
workflow.add_node("memory", memory_node)

workflow.set_entry_point("profiler")
workflow.add_edge("profiler", "detector")
workflow.add_edge("detector", "research")
workflow.add_edge("research", "advisor")
workflow.add_edge("advisor", "memory")
workflow.add_edge("memory", END)

scamshield_app = workflow.compile()
