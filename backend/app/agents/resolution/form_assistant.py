from langchain_core.prompts import ChatPromptTemplate
from backend.app.services.llm_provider import get_llm
from backend.app.schemas.resolution import IncidentDimensions

llm = get_llm(temperature=0.3)

form_fill_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a Legal Drafting Assistant.
    Your job is to write a clear, professional, and concise 'Incident Description' that the user can copy and paste into an official complaint form (FIR, Bank Dispute, Cybercrime Portal).
    
    Include:
    - Date/Time (Use placeholders if unknown)
    - Amount Lost (if financial)
    - Transaction IDs (if available)
    - Suspect details (if any)
    - Chronological flow of events.
    
    Keep it under 200 words if possible, as some forms have limits.
    Start directly with the text. Do not add conversational filler.
    """),
    ("user", """
    Incident Summary: {summary}
    Asset Affected: {asset}
    Attack Type: {attack}
    Urgency: {urgency}
    Controls: {controls}
    """)
])

def generate_form_text(dimensions: IncidentDimensions, summary: str) -> str:
    """Generates the copy-paste text for the complaint form."""
    chain = form_fill_prompt | llm
    res = chain.invoke({
        "summary": summary,
        "asset": str(dimensions.asset_affected),
        "attack": dimensions.attack_type,
        "urgency": dimensions.urgency,
        "controls": str(dimensions.control_authority)
    })
    return res.content
