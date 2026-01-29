from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.common import ScoutReport, UserProfile, Explanation
from backend.app.services.llm_provider import get_llm

llm = get_llm(temperature=0.7)

explain_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a cyber-guardian angel. You explain technical risks to normal people."),
    ("user", """
    The technical scout reported:
    Verdict: {verdict}
    Patterns: {patterns}
    
    AUTHENTIC RESEARCH FINDINGS (Live Web/Reddit/Twitter Data):
    {research_context}
    
    The user is:
    Type: {user_type}
    Language: {language}
    Style: {style}
    
    Draft a {language} explanation that is {style}.
    It should be comforting but firm if it's a scam.
    
    CRITICAL: If the RESEARCH FINDINGS confirm this is a active/trending scam (e.g., seen on Reddit/Twitter recently), explicitly mention that (e.g., "Our research confirms this is a widely reported scam currently targeting X..."). This adds authenticity.
    
    Return an Explanation object.
    """)
])

def generate_explanation(scout_report: ScoutReport, user_profile: UserProfile, research_context: str = "") -> Explanation:
    chain = explain_prompt | llm.with_structured_output(Explanation)
    return chain.invoke({
        "verdict": scout_report.verdict,
        "patterns": ", ".join(scout_report.detected_patterns),
        "research_context": research_context,
        "user_type": user_profile.user_type,
         # Fallback to English prompt instructions but request output in target language
        "language": user_profile.language, 
        "style": user_profile.explanation_style
    })
