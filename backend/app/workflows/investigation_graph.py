import json
from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END
from backend.app.services.vision_engine import VisionEngine, FraudEntityExtractor
from backend.app.services.audio_engine import AudioEngine

class InvestigationState(TypedDict):
    case_id: str
    input_text: Optional[str]
    image_base64: Optional[str]
    audio_bytes: Optional[bytes]
    vision_results: Optional[dict]
    audio_results: Optional[dict]
    extracted_entities: Optional[dict]
    timeline_events: Optional[list]
    scam_patterns: Optional[list]
    legal_draft: Optional[str]

# --- Nodes ---

async def vlm_analysis_node(state: InvestigationState):
    if state.get("image_base64"):
        vision = VisionEngine()
        res = await vision.analyze_screenshot(state["image_base64"])
        state["vision_results"] = res
    return state

async def audio_analysis_node(state: InvestigationState):
    if state.get("audio_bytes"):
        audio = AudioEngine()
        res = await audio.analyze_audio(state["audio_bytes"], "upload.mp3")
        state["audio_results"] = res
    return state

async def ocr_extraction_node(state: InvestigationState):
    extractor = FraudEntityExtractor()
    text_to_analyze = state.get("input_text", "")
    
    if state.get("vision_results") and "extracted_text" in state["vision_results"]:
        text_to_analyze += " " + state["vision_results"]["extracted_text"].get("raw_text", "")
        
    if state.get("audio_results") and "transcript" in state["audio_results"]:
        text_to_analyze += " " + state["audio_results"]["transcript"]
        
    if text_to_analyze.strip():
        entities = await extractor.extract_entities(text_to_analyze)
        state["extracted_entities"] = entities
        
    return state

async def scam_search_node(state: InvestigationState):
    # Mocking search logic for now to avoid blocking the graph on DB failure
    state["scam_patterns"] = [{"pattern": "Detected urgency and fake link."}]
    return state

async def timeline_node(state: InvestigationState):
    # Mocking timeline generation
    state["timeline_events"] = [{"time": "Now", "event": "Analysis completed"}]
    return state

async def legal_draft_node(state: InvestigationState):
    # Mocking Legal Draft
    state["legal_draft"] = "DRAFT FIR: I would like to report a cybercrime incident..."
    return state

# --- Graph Definition ---

workflow = StateGraph(InvestigationState)

workflow.add_node("vlm_analysis", vlm_analysis_node)
workflow.add_node("audio_analysis", audio_analysis_node)
workflow.add_node("ocr_extraction", ocr_extraction_node)
workflow.add_node("scam_search", scam_search_node)
workflow.add_node("timeline", timeline_node)
workflow.add_node("legal_draft", legal_draft_node)

workflow.set_entry_point("vlm_analysis")
workflow.add_edge("vlm_analysis", "audio_analysis")
workflow.add_edge("audio_analysis", "ocr_extraction")
workflow.add_edge("ocr_extraction", "scam_search")
workflow.add_edge("scam_search", "timeline")
workflow.add_edge("timeline", "legal_draft")
workflow.add_edge("legal_draft", END)

investigation_graph = workflow.compile()
