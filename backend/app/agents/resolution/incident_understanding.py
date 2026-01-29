from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.resolution import IncidentDimensions
from backend.app.services.llm_provider import get_llm
from typing import Optional, Dict

llm = get_llm(temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert cyber incident classifier. Your job is to extract the 5 universal dimensions of a cybercrime from a user's description."),
    ("user", """
    User Description: {description}
    User Context: {context}
    
    Analyze and return the IncidentDimensions JSON.
    Infere specific control authorities (e.g. 'Bank', 'Instagram', 'Police') based on the description.
    """)
])

from langchain_core.output_parsers import JsonOutputParser

def understand_incident(description: str, context: Optional[Dict] = None) -> IncidentDimensions:
    parser = JsonOutputParser(pydantic_object=IncidentDimensions)
    format_instructions = parser.get_format_instructions()
    
    debug_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert cyber incident classifier. Your job is to extract the 5 universal dimensions of a cybercrime from a user's description.\n{format_instructions}"),
        ("user", """
        User Description: {description}
        User Context: {context}
        
        Analyze and return the IncidentDimensions JSON.
        - Extract 3 key prevention tips for the future.
        - Explain the logic (mechanism) of the attack briefly.
        - Infere specific control authorities (e.g. 'Bank', 'Instagram', 'Police').
        """)
    ])
    
    chain = debug_prompt | llm | parser
    
    try:
        print("--- DEBUG: Understanding Incident ---")
        result = chain.invoke({
            "description": description, 
            "context": str(context),
            "format_instructions": format_instructions
        })
        print(f"--- DEBUG: Incident Dimensions: {result} ---")
        return IncidentDimensions(**result)
    except Exception as e:
        print(f"--- INCIDENT AGENT ERROR: {e} ---")
        # Fallback
        return IncidentDimensions(
            asset_affected=["unknown"],
            attack_type="unknown",
            control_authority=["Cyber Crime Portal"],
            urgency="medium",
            summary="Error understanding incident.",
            prevention_tips=["Contact authorities", "Secure accounts"],
            incident_logic="Unknown error in analysis"
        )
