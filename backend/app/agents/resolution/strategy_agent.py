from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.resolution import ResolutionStrategy, IncidentDimensions, ResolutionStep
from backend.app.mcp_servers.resolution_knowledge.server import get_playbook
from backend.app.services.llm_provider import get_llm
import uuid

llm = get_llm(temperature=0.3)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strategic crisis manager. Create a tailored step-by-step resolution plan."),
    ("user", """
    Incident Dimensions: {dimensions}
    
    Generic Playbook for Attack Type: {playbook}
    
    Create a ResolutionStrategy.
    - Break down the generic playbook into specific, actionable steps for this user.
    - Assign a unique step_id.
    - Categorize each step into the correct phase (containment, securing, reporting, recovery, prevention).
    - Estimate the timeline.
    """)
])

from langchain_core.output_parsers import JsonOutputParser

def create_strategy(dimensions: IncidentDimensions, research_context: str = "") -> ResolutionStrategy:
    playbook = get_playbook(dimensions.attack_type)
    
    parser = JsonOutputParser(pydantic_object=ResolutionStrategy)
    format_instructions = parser.get_format_instructions()
    
    debug_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a strategic crisis manager. Create a tailored step-by-step resolution plan.\n{format_instructions}"),
        ("user", """
        Incident Dimensions: {dimensions}
        
        AUTHENTIC RESEARCH FINDINGS (Use these for specific links/forms):
        {research_context}
        
        Generic Playbook for Attack Type: {playbook}
        
        Create a ResolutionStrategy.
        - Break down the generic playbook into specific, actionable steps for this user.
        - **CRITICAL**: Use the RESEARCH FINDINGS to replace generic advice with specific, verified steps and links found online/on Reddit/Twitter.
        - Assign a unique step_id.
        - Categorize each step into the correct phase (containment, securing, reporting, recovery, prevention).
        - Estimate the timeline.
        """)
    ])
    
    chain = debug_prompt | llm | parser
    
    try:
        print("--- DEBUG: Generating Resolution Strategy ---")
        result = chain.invoke({
            "dimensions": dimensions.model_dump(), 
            "playbook": playbook,
            "research_context": research_context,
            "format_instructions": format_instructions
        })
        print(f"--- DEBUG: Strategy Result: {result} ---")
        return ResolutionStrategy(**result)
    except Exception as e:
        print(f"--- STRATEGY AGENT ERROR: {e} ---")
        # Return a safe fallback so the graph doesn't crash, 
        # but tasks will be empty (user will see 'No tasks').
        # Better to return at least one generic step.
        return ResolutionStrategy(
            lifecycle_plan=[], 
            estimated_timeline="Error generating plan."
        )
