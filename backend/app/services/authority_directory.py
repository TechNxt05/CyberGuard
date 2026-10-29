import requests
import os
from typing import Dict
from pydantic import BaseModel

from app.services.official_sources import OFFICIAL_DOMAINS


# --- Static Registry of Verified Official Links ---
# This prevents hallucinations and phishing.
VERIFIED_AUTHORITIES = {
    "cybercrime.gov.in": {
        "name": "National Cyber Crime Reporting Portal",
        "home": "https://cybercrime.gov.in/",
        "file_complaint": "https://cybercrime.gov.in/Accept.aspx",
        "track_complaint": "https://cybercrime.gov.in/CheckStatus.aspx"
    },
    "1930": {
        "name": "Citizen Financial Cyber Fraud Reporting Management System",
        "phone": "1930",
        "description": "Call immediately for financial fraud."
    },
    "rbi_ombudsman": {
        "name": "RBI Ombudsman",
        "home": "https://cms.rbi.org.in/",
        "file_complaint": "https://cms.rbi.org.in/"
    },
    "instagram": {
        "name": "Instagram Help Center",
        "hacked_account": "https://www.instagram.com/hacked/"
    },
    "facebook": {
        "name": "Facebook Hacked Help",
        "hacked_account": "https://www.facebook.com/hacked"
    },
    "whatsapp": {
        "name": "WhatsApp Grievance Officer",
        "contact": "https://www.whatsapp.com/contact"
    }
}

class AuthorityInfo(BaseModel):
    name: str
    official_urls: Dict[str, str]
    is_verified: bool
    status: str = "unknown"

def get_official_link(key: str) -> Dict:
    """
    Retrieves verified links for a known authority (e.g., 'instagram', 'cybercrime.gov.in', 'rbi').
    Returns dictionary with URLs or error.
    """
    key = key.lower().replace(" ", "")
    if len(key) < 3:
        return {"error": "Authority not found in verified registry."}
    # Registry key contained in the query (e.g. "instagram" in "instagramsupport"), or vice versa for longer queries
    for k, v in VERIFIED_AUTHORITIES.items():
        if k in key or (len(key) >= 5 and key in k):
            return v
    # Fall back to the wider official-domain list (banks, payment apps, platforms, couriers, telecom).
    generic = {"bank", "national", "union", "india", "punjab", "google", "x"}
    for name, domains in OFFICIAL_DOMAINS.items():
        brand = name.lower().split()[0]
        full = name.lower().split("(")[0].replace(" ", "")
        if (brand not in generic and brand in key) or full in key:
            return {"name": name, "home": f"https://{domains[0]}"}
    return {"error": "Authority not found in verified registry."}

def check_website_status(url: str) -> str:
    """Verifies if a website is reachable."""
    try:
        # User-Agent is often required for security checks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return "Online"
        return f"Down (Status: {response.status_code})"
    except Exception as e:
        return f"Unreachable ({str(e)})"

def find_nodal_officer(bank_name: str, location: str = "India") -> str:
    """
    Uses SerpApi to find the specific Nodal Officer contact PDF or page for a bank.
    Requires SERPAPI_API_KEY env var (optional; returns "" when not configured).
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        return ""
    
    query = f"{bank_name} nodal officer for cyber fraud {location} filetype:pdf OR site:{bank_name.lower()}.com"
    
    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": 3
    }
    
    try:
        # Direct HTTP call to avoid extra dependencies
        res = requests.get("https://serpapi.com/search", params=params, timeout=10)
        data = res.json()
        
        results = []
        if "organic_results" in data:
            for item in data["organic_results"]:
                results.append(f"- {item.get('title')}: {item.get('link')}")
                
        if results:
            return "Found potential contacts:\n" + "\n".join(results)
        return "No specific nodal officer documents found."
        
    except Exception:
        return ""
