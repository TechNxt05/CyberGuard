import re


def extract_entities(text: str) -> dict:
    """Fast, deterministic regex extraction of fraud indicators (no LLM)."""
    entities = {
        "upi_id": [],
        "phone_number": [],
        "url": [],
        "email": [],
        "wallet_address": []
    }
    if not text:
        return entities

    # UPI IDs: pattern@provider
    upi_pattern = r'\b[\w.-]+@(?:ybl|paytm|upi|okaxis|okhdfcbank|oksbi|okicici|apl|ibl|pingpay|slice)\b'
    upis = re.findall(upi_pattern, text, re.IGNORECASE)
    if upis:
        entities["upi_id"] = list(set(upis))

    # Phone numbers: Indian 10-digit
    phone_pattern = r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b'
    phones = re.findall(phone_pattern, text)
    if phones:
        entities["phone_number"] = list(set([re.sub(r'[\s-]', '', p) for p in phones]))

    # URLs, plus bare domains like "sbi-kyc-update.in/verify" that scam SMSes often use
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    urls = re.findall(url_pattern, text)
    remainder = re.sub(url_pattern, " ", text)
    bare_pattern = r'(?<![@\w.-])(?:[a-z0-9-]+\.)+(?:com|in|net|org|xyz|top|info|co|io|app|link|online|site|club|live|shop)(?:/[^\s<>"]*)?(?![\w@])'
    urls += re.findall(bare_pattern, remainder, re.IGNORECASE)
    if urls:
        entities["url"] = list(set(u.rstrip(".,);") for u in urls))

    # Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    if emails:
        entities["email"] = list(set(emails))

    # Crypto wallet addresses (Bitcoin: 26-35 chars starting with 1/3/bc1)
    wallet_pattern = r'\b(?:1[a-km-zA-HJ-NP-Z1-9]{25,34}|3[a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-z0-9]{39,59})\b'
    wallets = re.findall(wallet_pattern, text)
    if wallets:
        entities["wallet_address"] = list(set(wallets))

    return entities
