from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.common import ScoutReport, UserProfile
from backend.app.mcp_servers.scam_knowledge.server import search_scam_patterns, get_scam_rules
from backend.app.services.llm_provider import get_llm

# In a real distributed MCP setup, we would call these via an MCP Client.
# For this MVP monorepo struct, we directly import the functions decorated as tools,
# respecting the "Agent decides to call tool" pattern.

llm = get_llm(temperature=0.2)

from langchain_core.messages import HumanMessage

# ... imports remain same

detection_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a ruthlessly efficient scam detection expert. Use the provided context and rules to judge the message."),
    ("user", """
    Analyze this message: "{message}"
    
    Context from Knowledge Base (Similar Scams):
    {similar_patterns}
    
    Known Scam Rules:
    {rules}
    
    User Profile: {user_profile}
    
    Provide a ScoutReport in JSON with:
    - risk_score: 0-100
    - scam_type: classic category
    - analysis: brief summary
    - scam_logic: EXACTLY how the trick works (e.g. "Creates false urgency/fear")
    - consequences: EXACTLY what they will lose (e.g. "Will drain bank account via APK")
    - recommendation: Clear DO and DON'T
    - severity: critical/high/medium/low/safe
    - extracted_entities: JSON dict of key details if any
    """)
])

def detect_scam(message: str | None, user_profile: UserProfile, image_base64: str | None = None) -> ScoutReport:
    # 1. Handle Image Input: If image exists but no text, extract text first.
    if image_base64 and not message:
        # FORCE GEMINI FOR VISION (Groq cannot handle images)
        from langchain_google_genai import ChatGoogleGenerativeAI
        import os
        
        vision_llm = None
        if os.getenv("GEMINI_API_KEY"):
             vision_llm = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GEMINI_API_KEY"),
                model="gemini-1.5-flash",
                temperature=0.1
             )
        
        if vision_llm:
            try:
                # Ask LLM to describe/extract text from image
                ocr_message = HumanMessage(
                    content=[
                        {"type": "text", "text": "Extract all readable text from this screenshot. If it looks like a scam message, describe the visual context (e.g. logos, urgency)."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                    ]
                )
                msg_response = vision_llm.invoke([ocr_message])
                message = msg_response.content
            except Exception as e:
                print(f"Vision Error: {e}")
                message = "Error analyzing image. Please text instead."
        else:
             message = "Image analysis unavailable (No Gemini Key)."
    
    # Fallback if still empty
    
    # Fallback if still empty
    if not message:
        message = "No content detected."

    # 2. Proceed with standard flow (RAG + Analysis)
    similar_patterns = search_scam_patterns(message)
    rules = get_scam_rules()
    
    # DEBUGGING: Switch to manual parsing to see raw output
    from langchain_core.output_parsers import JsonOutputParser
    
    parser = JsonOutputParser(pydantic_object=ScoutReport)
    
    # Update prompt to include format instructions
    format_instructions = parser.get_format_instructions()
    
    debug_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a ruthlessly efficient scam detection expert. Use the provided context and rules to judge the message.\n{format_instructions}"),
        ("user", """
        Analyze this message: "{message}"
        
        Context from Knowledge Base (Similar Scams):
        {similar_patterns}
        
        Known Scam Rules:
        {rules}
        
        User Profile: {user_profile}
        
        Provide a ScoutReport in JSON with:
        - risk_score: 0-100
        - scam_type: classic category
        - analysis: brief summary
        - scam_logic: EXACTLY how the trick works
        - consequences: EXACTLY what they will lose
        - recommendation: Clear DO and DON'T
        - severity: critical/high/medium/low/safe
        - extracted_entities: JSON dict of key details if any
        """)
    ])
    
    chain = debug_prompt | llm | parser
    
    try:
        print("--- DEBUG: Invoking LLM for Scam Detection ---")
        result = chain.invoke({
            "message": message,
            "similar_patterns": similar_patterns,
            "rules": rules,
            "user_profile": user_profile.model_dump(),
            "format_instructions": format_instructions
        })
        print(f"--- DEBUG: LLM Result: {result} ---")
        return ScoutReport(**result)
    except Exception as e:
        print(f"--- CRITICAL LLM ERROR: {e} ---")
        # Fallback Safe Report
        return ScoutReport(
            scam_probability=0,
            verdict="SAFE",
            risk_score=0,
            scam_logic="Analysis failed. Please try again.",
            consequences="Unknown",
            severity="safe",
            recommendation="Proceed with caution.",
            extracted_entities={}
        )
