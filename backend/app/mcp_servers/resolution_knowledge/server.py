from mcp.server.fastmcp import FastMCP
from typing import List, Dict, Any
import json

mcp = FastMCP("ResolutionKnowledge")

# Mock Knowledge Base (In production, this would be a real DB or detailed JSON file)
PLAYBOOKS = {
    "fraud": {
        "containment": ["Freeze associated accounts immediately.", "Change passwords if credentials were shared."],
        "securing": ["Enable 2FA on all accounts.", "Check for suspicious forwarding rules/devices."],
        "reporting": ["Report to 1930 (Cybercrime Helpline).", "File an FIR or online complaint.", "Dispute transaction with Bank/Platform."],
        "recovery": ["Follow up with bank for chargeback.", "Monitor credit report."],
        "prevention": ["Learn about social engineering.", "Use separate accounts for daily UPI."]
    },
    "unauthorized_access": {
        "containment": ["Log out of all active sessions.", "Revoke app permissions."],
        "securing": ["Change password to a strong passphrase.", "Enable hardware key or authenticator app."],
        "reporting": ["Report compromise to the platform support.", "Notify contacts to ignore messages."],
        "recovery": [" reclaim account via recovery codes/ID verification.", "Clean device with antivirus."],
        "prevention": ["Use a password manager.", "Don't click suspicious links."]
    },
    "sextortion": {
        "containment": ["Do NOT pay the ransom (they will ask for more).", "Block the scammer immediately on all platforms."],
        "securing": ["Deactivate social media accounts temporarily.", "Change privacy settings to strict."],
        "reporting": ["Report profile to the platform (Instagram/Facebook).", "File complaint at cybercrime.gov.in."],
        "recovery": ["Seek emotional support/counseling.", "If content leaked, use StopNCII.org to remove images."],
        "prevention": ["Never share intimate images online.", "Be wary of strangers asking for video calls."]
    },
    "ransomware": {
        "containment": ["Disconnect device from internet/network immediately.", "Power off to stop encryption."],
        "securing": ["Isolate infected systems.", "Reset credentials for all networks."],
        "reporting": ["Report to CERT-In or Cyber Police.", "Do not communicate with attackers."],
        "recovery": ["Restore data from offline backups.", "Use 'No More Ransom' tools to attempt decryption."],
        "prevention": ["Regular offline backups.", "Keep OS and antivirus updated."]
    },
    "job_fraud": {
        "containment": ["Stop all communication with the 'recruiter'.", "Do not pay any more 'processing fees'."],
        "securing": ["If bank details shared, inform bank to freeze.", "Monitor accounts for unauthorized debit."],
        "reporting": ["Report the job posting on the platform (LinkedIn/Naukri).", "File FIR."],
        "recovery": ["Warn others by reviewing the company online.", "Request refund from gateway if possible."],
        "prevention": ["Legit jobs never ask for money to join.", "Check company email domain."]
    },
    "courier_scam": {
        "containment": ["Disconnect the call immediately.", "Do NOT download any support apps (AnyDesk/TeamViewer)."],
        "securing": ["Uninstall any remote access apps installed.", "Change netbanking passwords."],
        "reporting": ["Report number to Chakshu Portal (Sanchar Saathi).", "Call 1930."],
        "recovery": ["Contact bank immediately if money deducted.", "File dispute."],
        "prevention": ["Verify tracking number on official website manually.", "Police/Customs never call via Skype."]
    }
}

AUTHORITY_MAP = {
    "India": {
        "financial_fraud": {"name": "Cyber Crime Portal", "contact": {"phone": "1930", "url": "cybercrime.gov.in"}, "docs": ["Transaction ID", "Bank Statement"]},
        "bank": {"name": "RBI Ombudsman", "contact": {"url": "cms.rbi.org.in"}, "docs": ["Complaint Number"]},
    },
    "Global": {
        "social_media": {"name": "Platform Support", "contact": {"note": "Use in-app help center"}, "docs": ["ID Proof"]}
    }
}

@mcp.tool()
def get_playbook(attack_type: str) -> Dict[str, List[str]]:
    """
    Returns a generic lifecycle playbook for a given attack type.
    """
    return PLAYBOOKS.get(attack_type, PLAYBOOKS.get("fraud"))

@mcp.tool()
def identify_authorities(context: str, domain: str) -> Dict[str, Any]:
    """
    Returns specific authority contact info based on user context (e.g. Country) and domain (e.g. 'bank', 'social_media').
    Context is expected to be a JSON string or key like 'India'.
    """
    # Simple MVP logic
    if "India" in context:
        return AUTHORITY_MAP["India"].get(domain, {})
    return AUTHORITY_MAP["Global"].get(domain, {})

if __name__ == "__main__":
    mcp.run()
