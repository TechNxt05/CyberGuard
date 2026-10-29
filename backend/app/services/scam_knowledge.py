"""
Small in-process scam pattern knowledge base.

Similarity is TF-IDF cosine over word unigrams + bigrams, implemented in pure Python so it
adds no heavy dependencies (faiss / sentence-transformers don't fit Render's free 512 MB).
"""
import math
import re
from collections import Counter

# Seed corpus of common (mostly Indian) scam patterns
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


_TOKEN_RE = re.compile(r"[a-z0-9]+")
_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "can", "do", "for", "from", "has", "have", "hi", "hello",
    "how", "i", "if", "in", "is", "it", "me", "my", "no", "not", "of", "on", "or", "so", "the", "this", "to",
    "we", "what", "why", "will", "with", "you", "your",
}


def _tokens(text: str) -> list[str]:
    words = [w for w in _TOKEN_RE.findall(text.lower()) if w not in _STOPWORDS]
    return words + [f"{a}_{b}" for a, b in zip(words, words[1:])]


def _build_index(corpus: list[str]):
    docs = [Counter(_tokens(t)) for t in corpus]
    df = Counter(term for doc in docs for term in doc)
    idf = {term: math.log((1 + len(docs)) / (1 + count)) + 1 for term, count in df.items()}
    vectors = [_weigh(doc, idf) for doc in docs]
    return idf, vectors


def _weigh(counts: Counter, idf: dict) -> dict:
    vec = {t: c * idf.get(t, 0.0) for t, c in counts.items() if t in idf}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {t: v / norm for t, v in vec.items()}


_IDF, _VECTORS = _build_index(seed_data)


def search_scam_patterns(text: str, top_k: int = 3, min_score: float = 0.05) -> list[str]:
    """Returns up to `top_k` known scam patterns most similar to `text` (empty if nothing is similar)."""
    query = _weigh(Counter(_tokens(text)), _IDF)
    scored = []
    for pattern, vec in zip(seed_data, _VECTORS):
        score = sum(weight * vec.get(term, 0.0) for term, weight in query.items())
        if score >= min_score:
            scored.append((score, pattern))
    scored.sort(reverse=True)
    return [pattern for _, pattern in scored[:top_k]]


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
