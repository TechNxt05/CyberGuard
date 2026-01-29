from langchain_core.prompts import ChatPromptTemplate
from backend.app.schemas.resolution import IncidentDimensions, AuthorityContact
from backend.app.services.llm_provider import get_llm
from typing import List, Dict

llm = get_llm(temperature=0.1)

# In a real agent, the LLM would decide WHICH tool to call.
# Here for MVP, we use the LLM to refine the tool output or directly map logic.

def map_authorities(dimensions: IncidentDimensions, user_context: Dict[str, str] = None) -> List[AuthorityContact]:
    """
    Identifies specific authorities and contacts.
    """
    authorities = []
    context_str = "India" if not user_context else user_context.get("country", "India")
    
    
    # Imports for new data sources
    from backend.app.mcp_servers.authority_source.server import get_official_link, find_nodal_officer

    # 1. Financial Fraud / General Cybercrime
    if "money" in dimensions.asset_affected or "fraud" == dimensions.attack_type:
        auth_data = get_official_link("cybercrime.gov.in")
        contact_info = {"url": auth_data.get("file_complaint", "https://cybercrime.gov.in")}
        
        # 1930 Helpline
        helpline = get_official_link("1930")
        contact_info["phone"] = helpline.get("phone")
        
        authorities.append(AuthorityContact(
            name="National Cyber Crime Reporting Portal",
            role="Law Enforcement",
            contact_info=contact_info,
            required_documents=["Transaction ID", "Bank Statement", "ID Proof"]
        ))
            
    # 2. Specific Control Authorities (Banks, Social Media)
    for Auth in dimensions.control_authority:
        auth_key = Auth.lower()
        contact_info = {}
        
        # Check Static Registry first
        static_data = get_official_link(auth_key)
        if "error" not in static_data:
            contact_info = static_data
            role = "Verified Official Portal"
        else:
            # Fallback: Dynamic Search for Nodal Officers (SerpApi)
            # This is the "Exact Solution" feature for small banks
            search_result = find_nodal_officer(Auth, "India") # Defaulting to India for MVP
            contact_info = {"search_result": search_result}
            role = "Nodal Officer / Dynamic Lookup"

        authorities.append(AuthorityContact(
            name=f"{Auth} Resolution Authority",
            role=role,
            contact_info=contact_info,
            required_documents=["Account Details", "Proof of ownerhsip"]
        ))
                  
    return authorities
                 
    return authorities
