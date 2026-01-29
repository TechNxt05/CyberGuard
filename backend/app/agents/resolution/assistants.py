from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.resolution import ResolutionStep
from backend.app.services.llm_provider import get_llm
from typing import List, Optional

llm = get_llm(temperature=0.5)

# --- Guide Agent ---
guide_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a patient, step-by-step technical guide."),
    ("user", """
    Expand this single resolution step into a micro-guide:
    Step: {step_description}
    Action: {step_action}
    
    Provide 3-5 very short, clear sentences on exactly how to do this.
    """)
])

def guide_step(step: ResolutionStep) -> str:
    chain = guide_prompt | llm
    result = chain.invoke({
        "step_description": step.description, 
        "step_action": step.action
    })
    return result.content

# --- Form/Evidence Assistant ---
form_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a legal aid assistant helping users prepare complaints."),
    ("user", """
    The user needs to perform this action: {action}
    Required documents/info typically involved: {docs}
    
    Draft a template text or a checklist of evidence they need to gather before starting.
    """)
])

def assist_form(action: str, docs: Optional[List[str]] = None) -> str:
    chain = form_prompt | llm
    result = chain.invoke({"action": action, "docs": str(docs)})
    return result.content

# --- Doubt Resolution ---
doubt_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a reassuring expert answering user concerns."),
    ("user", "User Question: {question}\nContext (Current Plan): {plan_summary}\n\nAnswer the user.")
])

def resolve_doubt(question: str, plan_summary: str) -> str:
    chain = doubt_prompt | llm
    result = chain.invoke({"question": question, "plan_summary": plan_summary})
    return result.content
