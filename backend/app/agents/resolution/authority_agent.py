from typing import Dict, List

from app.schemas.resolution import AuthorityContact, IncidentDimensions
from app.services.authority_directory import find_nodal_officer, get_official_link


def map_authorities(dimensions: IncidentDimensions, user_context: Dict[str, str] = None) -> List[AuthorityContact]:
    """
    Identifies specific authorities and contacts.
    """
    authorities = []
    country = (user_context or {}).get("country", "India")

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
            contact_info={k: str(v) for k, v in contact_info.items()},
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
            # Fallback: dynamic search for the institution's nodal/grievance officer (only if SerpApi is configured)
            search_result = find_nodal_officer(Auth, country)
            if search_result:
                contact_info = {"search_result": search_result}
                role = "Nodal Officer / Dynamic Lookup"
            else:
                contact_info = {"note": f"Use the 'Grievance' or 'Nodal Officer' page on {Auth}'s official website (type the address yourself; don't use links from messages)."}
                role = "Official Grievance Channel"

        authorities.append(AuthorityContact(
            name=f"{Auth} Resolution Authority",
            role=role,
            contact_info={k: str(v) for k, v in contact_info.items()},
            required_documents=["Account Details", "Proof of ownership"]
        ))
                  
    return authorities
