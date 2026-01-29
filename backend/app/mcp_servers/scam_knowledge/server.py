from mcp.server.fastmcp import FastMCP
import faiss
import numpy as np
import pickle
import os

# Initialize FastMCP Scraper
mcp = FastMCP("ScamKnowledge")

# Mock embedding function for MVP (Replace with sentence-transformers or OpenAI later)
def get_embedding(text: str):
    # Deterministic "features" for MVP based on keyword hashes to simulate vector space
    # In production, use: openai.Embedding.create(input=text)
    np.random.seed(sum(ord(c) for c in text[:10])) 
    return np.random.rand(128).astype('float32')

# In-memory vector store (FAISS)
d = 128
index = faiss.IndexFlatL2(d)
stored_patterns = []

# Pre-seed with some Indian scam patterns
seed_data = [
    "Dear customer your KY C is pending. Update immediately by clicking bit.ly/...",
    "Electricity bill unpaid. Power will be cut tonight. Call 98XXXXXXX",
    "Part time job offer. Earn 5000 daily. Just like youtube videos. WhatsApp now.",
    "Congratulations! You won a lottery of 25 Lakhs from KBC. Call Mr. Rana.",
    "Friend in hospital need urgent money UPI. Please help.",
    "This is Mumbai Police. Drgus found in your parcel. Connect to Skype immediately.",
    "Instant Loan approved 50,000. Low interest. Install App now.",
    "Scan this QR code to receive Rs 2000 in your account. Do not share PIN.",
    "Hi Handsome, why so lonely? Video call me for fun.",
    "Airtel 5G upgrade offer. Send SMS 'SIM 1234' to 121 to activate.",
    "Zomato Refund Customer Care. Call 99XXXXXXXX for refund.",
    "Crypto Trading Signals. 500% profit guaranteed in 24 hours. Join Telegram.",
    "Your computer has a virus. Call Microsoft Support Toll Free.",
    "Your files are encrypted. Pay 0.5 BTC to decrypt.",
    "Customs Duty pending for gift sent from UK. Pay immediately.",
    # Expanded Knowledge
    "You have been recorded watching adult content. Pay $500 or video will be sent to contacts. (Sextortion)",
    "FedEx: Your package is held at customs. Click here to pay duties: http://fake-link.com",
    "Amazon Hiring: Work from home, Rs 8000/day. No interview. Join WhatsApp group.",
    "HDFC Bank: Your account is blocked due to suspicious activity. Click to verify identity.",
    "Income Tax Refund approved. Click to claim your Rs 15,000 refund.",
    "Olx: I want to buy your furniture. I am army officer. sending QR code for advance payment.",
    "Facebook: Is this you in this video? [Link]",
    "Invest in Solar Energy. Double your money in 3 months. Government approved.",
    "Your Netflix subscription is expired. Update payment details immediately.",
    "Dad, I lost my phone. This is my new number. Send money for rent.",
    "Apple Support: suspicious login detected on your iCloud. Call support.",
    "Instagram: You have violated copyright. Verify account to avoid deletion.",
    "Deepfake video call from 'Boss' asking for urgent fund transfer.",
    "Free iPhone 15 Pro. Just pay shipping charges of Rs 199.",
    "Stock Market Tips: Insider news on penny stocks. 10x returns guaranteed.",
    "Work visa approved for Canada. Pay processing fee of 1 Lakh immediately.",
    "You missed a jury duty. Pay fine or arrest warrant will be issued.",
    "Tech Support: We found illegal pornograpy on your IP address. Pay fine.",
    " Dating App: I am stuck in customs. Can you pay the fee? I will return it."
]

for txt in seed_data:
    vec = get_embedding(txt)
    index.add(np.array([vec]))
    stored_patterns.append(txt)

@mcp.tool()
def search_scam_patterns(text: str, top_k: int = 3) -> list[str]:
    """
    Search for known scam patterns similar to the input text.
    Returns a list of similar scam texts found in the database.
    """
    vec = get_embedding(text)
    D, I = index.search(np.array([vec]), top_k)
    results = []
    for idx_val in I[0]:
        if idx_val < len(stored_patterns) and idx_val >= 0:
            results.append(stored_patterns[idx_val])
    return results

@mcp.tool()
def get_scam_rules() -> list[str]:
    """
    Returns strict rules for detecting scams (e.g., 'Never share OTP').
    """
    return [
        "Banks never ask for OTP or Password via call/SMS.",
        "Electricity board does not cut power without official notice.",
        "High returns with zero risk is always a scam.",
        "Urgency ('Do it NOW') is a major red flag.",
        "Unknown numbers asking for money for 'friends' are likely fake."
    ]

if __name__ == "__main__":
    mcp.run()
