from langchain_core.prompts import ChatPromptTemplate
from backend.app.services.llm_provider import get_llm

llm = get_llm(temperature=0.3)

# System Prompt with "Playbooks" for key sites
guidance_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a 'Website Navigation Guide' for Indian Cybercrime portals.
    Your goal is to give the user EXTREMELY specific, button-by-button instructions on how to navigate a specific website to file a complaint.
    
    You have knowledge of these standard flows:
    
    1. **Cybercrime.gov.in (National Portal)**:
       - Home Page -> Click "File a Complaint" (Red/Orange button).
       - Warning Page -> Click "I Accept".
       - Login/Register Page -> Suggest "Report Anonymously" if available, or "Click 'New User' to register" if they need to track it.
       - Incident Details -> Select "Category" (Financial/Social Media).
       
    2. **HDFC Bank Dispute**:
       - NetBanking -> 'Accounts' -> 'Transact' -> 'Debit Card' -> 'Dispute'.
       
    3. **Instagram Hacked**:
       - Go to instagram.com/hacked -> Select "My account was hacked" -> Click Next.
       
    For any other website, give best-guess generic instructions: "Look for 'Support', 'Grievance', or 'Fraud Reporting' links, usually in the footer."
    
    Output Format:
    Return a Markdown list of steps. Use bold for Button Names.
    Example:
    1. Go to **cybercrime.gov.in**.
    2. Click the red **File a Complaint** button on the home page.
    """),
    ("user", "Guide me through: {portal_name} for intent: {intent}")
])

def get_website_guide(portal_name: str, intent: str = "report_fraud") -> str:
    """Returns the visual step-by-step guide for the portal."""
    chain = guidance_prompt | llm
    res = chain.invoke({"portal_name": portal_name, "intent": intent})
    return res.content
