from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.common import ScoutReport, ActionPlan
from backend.app.services.llm_provider import get_llm

llm = get_llm(temperature=0.5)

response_prompt = ChatPromptTemplate.from_messages([
    ("system", "You provide concrete, actionable steps to stay safe."),
    ("user", """
    Verdict: {verdict}
    
    Give 3-4 bullet-point commands (Do's and Don'ts).
    If SCAM, include blocking instructions.
    
    Return an ActionPlan object.
    """)
])

def generate_action_plan(scout_report: ScoutReport) -> ActionPlan:
    chain = response_prompt | llm.with_structured_output(ActionPlan)
    return chain.invoke({"verdict": scout_report.verdict})
