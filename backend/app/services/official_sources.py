"""
Official domains for Indian government services, banks, payment apps and common platforms.

Used to (1) recognise legitimate links, (2) flag look-alike domains that borrow a brand name,
and (3) strip unverified links out of AI output that was influenced by web search results.
"""
import re
from urllib.parse import urlparse

OFFICIAL_DOMAINS: dict[str, list[str]] = {
    # Government / regulators
    "National Cybercrime Portal": ["cybercrime.gov.in"],
    "Sanchar Saathi (report fraud calls/SMS)": ["sancharsaathi.gov.in"],
    "RBI": ["rbi.org.in"],
    "NPCI / BHIM UPI": ["npci.org.in", "bhimupi.org.in"],
    "CERT-In": ["cert-in.org.in"],
    "Income Tax": ["incometax.gov.in"],
    "UIDAI (Aadhaar)": ["uidai.gov.in"],
    "India Post": ["indiapost.gov.in"],
    # Banks: RBI moved Indian banks to .bank.in (registrable only by verified banks); older domains kept for matching.
    "SBI": ["sbi.bank.in", "sbi.co.in", "onlinesbi.sbi"],
    "HDFC Bank": ["hdfc.bank.in", "hdfcbank.com"],
    "ICICI Bank": ["icici.bank.in", "icicibank.com"],
    "Axis Bank": ["axis.bank.in", "axisbank.com"],
    "Kotak Mahindra Bank": ["kotak.bank.in", "kotak.com"],
    "Punjab National Bank": ["pnb.bank.in", "pnbindia.in"],
    "Bank of Baroda": ["bankofbaroda.bank.in", "bankofbaroda.in"],
    "Canara Bank": ["canarabank.bank.in", "canarabank.com"],
    "Union Bank of India": ["unionbankofindia.bank.in", "unionbankofindia.co.in"],
    "Yes Bank": ["yes.bank.in", "yesbank.in"],
    "IDFC FIRST Bank": ["idfcfirst.bank.in", "idfcfirstbank.com"],
    "IndusInd Bank": ["indusind.bank.in", "indusind.com"],
    # Payments / shopping
    "Paytm": ["paytm.com"],
    "PhonePe": ["phonepe.com"],
    "Google Pay": ["pay.google.com", "google.com"],
    "Amazon": ["amazon.in", "amazon.com"],
    "Flipkart": ["flipkart.com"],
    # Platforms
    "WhatsApp": ["whatsapp.com"],
    "Instagram": ["instagram.com"],
    "Facebook": ["facebook.com"],
    "X / Twitter": ["x.com", "twitter.com"],
    "Telegram": ["telegram.org"],
    "Microsoft": ["microsoft.com"],
    "Apple": ["apple.com"],
    # Couriers / telecom
    "FedEx": ["fedex.com"],
    "DHL": ["dhl.com"],
    "Blue Dart": ["bluedart.com"],
    "Airtel": ["airtel.in"],
    "Jio": ["jio.com"],
    "BSNL": ["bsnl.co.in"],
}

# Brand keywords that scammers put into look-alike domains (e.g. "sbi-kyc-update.in").
BRAND_KEYWORDS: dict[str, str] = {
    "sbi": "SBI", "hdfc": "HDFC Bank", "icici": "ICICI Bank", "axisbank": "Axis Bank", "kotak": "Kotak Mahindra Bank",
    "pnb": "Punjab National Bank", "bankofbaroda": "Bank of Baroda", "canara": "Canara Bank", "paytm": "Paytm",
    "phonepe": "PhonePe", "gpay": "Google Pay", "googlepay": "Google Pay", "amazon": "Amazon", "flipkart": "Flipkart",
    "whatsapp": "WhatsApp", "instagram": "Instagram", "facebook": "Facebook", "fedex": "FedEx", "dhl": "DHL",
    "bluedart": "Blue Dart", "indiapost": "India Post", "airtel": "Airtel", "jio": "Jio", "rbi": "RBI",
    "npci": "NPCI / BHIM UPI", "uidai": "UIDAI (Aadhaar)", "aadhaar": "UIDAI (Aadhaar)", "incometax": "Income Tax",
    "cybercrime": "National Cybercrime Portal", "trai": "TRAI",
}

_ALL_OFFICIAL = {d for domains in OFFICIAL_DOMAINS.values() for d in domains}
# Explicit URLs, plus bare domains with common TLDs (a fixed TLD list avoids matching file names like "statement.pdf").
_URL_RE = re.compile(
    r'(?:https?://|www\.)[^\s<>"\')\]]+'
    r'|(?<![@\w.-])(?:[a-z0-9-]+\.)+(?:com|in|net|org|xyz|top|info|co|io|app|link|online|site|club|live|shop|me|biz|sbi|bank)\b(?:/[^\s<>"\')\]]*)?',
    re.IGNORECASE,
)
_SECOND_LEVEL = {"co", "org", "net", "gov", "ac", "gen", "firm", "ind", "edu", "nic", "res"}


def domain_of(url: str) -> str:
    url = url.strip().rstrip(".,;)")
    if "://" not in url:
        url = "http://" + url
    host = (urlparse(url).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def registrable_domain(host: str) -> str:
    """Best-effort eTLD+1 (handles .co.in, .gov.in and similar)."""
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in _SECOND_LEVEL:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def is_official(host: str) -> bool:
    host = host.lower()
    if host.endswith((".gov.in", ".nic.in", ".bank.in")):
        return True
    return any(host == d or host.endswith("." + d) for d in _ALL_OFFICIAL)


def impersonated_brand(host: str) -> str | None:
    """Brand a non-official domain appears to imitate, if any."""
    if is_official(host):
        return None
    labels = re.split(r"[.-]", host.lower())[:-1]  # ignore the TLD
    for label in labels:
        for keyword, brand in BRAND_KEYWORDS.items():
            if keyword in label:
                return brand
    return None


def sanitize_links(text: str) -> str:
    """Removes links that are not on an official domain (protects against injected links from web results)."""
    if not text:
        return text

    def _replace(match: re.Match) -> str:
        candidate = match.group(0)
        host = domain_of(candidate)
        if not host or "." not in host or is_official(host):
            return candidate
        return "[link removed - use only the official website]"

    return _URL_RE.sub(_replace, text)


def official_links_text() -> str:
    return "\n".join(f"- {name}: {', '.join(domains)}" for name, domains in OFFICIAL_DOMAINS.items())
