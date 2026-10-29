"""
Deterministic link checks - hard evidence that doesn't depend on an LLM's judgement.

- Domain age via RDAP (free, no key): a days-old domain using a bank's name is a strong scam signal.
- Look-alike detection against the official-domain list.
- Google Safe Browsing (free key, optional: GOOGLE_SAFE_BROWSING_KEY).
- URLhaus by abuse.ch (free key, optional: URLHAUS_AUTH_KEY).
"""
import concurrent.futures
import logging
import os
import time
from datetime import datetime, timezone

import httpx

from app.services.entity_extraction import extract_entities
from app.services.official_sources import domain_of, impersonated_brand, is_official, registrable_domain

logger = logging.getLogger(__name__)

_TIMEOUT = 6
_YOUNG_DOMAIN_DAYS = 90
_MAX_URLS = 5
_CACHE_TTL = 24 * 60 * 60
_cache: dict[str, tuple[float, dict]] = {}


def _rdap_registration_date(domain: str) -> datetime | None:
    try:
        resp = httpx.get(f"https://rdap.org/domain/{domain}", timeout=_TIMEOUT, follow_redirects=True)
        if resp.status_code != 200:
            return None
        for event in resp.json().get("events", []):
            if event.get("eventAction") == "registration" and event.get("eventDate"):
                return datetime.fromisoformat(event["eventDate"].replace("Z", "+00:00"))
    except Exception as e:
        logger.info("RDAP lookup failed for %s: %s", domain, e)
    return None


def _safe_browsing_hit(url: str) -> bool | None:
    key = os.getenv("GOOGLE_SAFE_BROWSING_KEY")
    if not key:
        return None
    body = {
        "client": {"clientId": "cyberguard", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url if "://" in url else f"http://{url}"}],
        },
    }
    try:
        resp = httpx.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={key}", json=body, timeout=_TIMEOUT)
        return bool(resp.json().get("matches")) if resp.status_code == 200 else None
    except Exception as e:
        logger.info("Safe Browsing lookup failed: %s", e)
        return None


def _urlhaus_hit(host: str) -> bool | None:
    key = os.getenv("URLHAUS_AUTH_KEY")
    if not key:
        return None
    try:
        resp = httpx.post("https://urlhaus-api.abuse.ch/v1/host/", data={"host": host}, headers={"Auth-Key": key}, timeout=_TIMEOUT)
        return resp.json().get("query_status") == "ok" if resp.status_code == 200 else None
    except Exception as e:
        logger.info("URLhaus lookup failed: %s", e)
        return None


def check_url(url: str) -> dict:
    host = domain_of(url)
    cached = _cache.get(host)
    if cached and time.time() - cached[0] < _CACHE_TTL:
        return {**cached[1], "url": url}

    result: dict = {"url": url, "domain": host, "verdict": "unknown", "signals": []}
    if not host or "." not in host:
        return result

    if is_official(host):
        result.update(verdict="official", signals=["Official domain"])
    else:
        brand = impersonated_brand(host)
        if brand:
            result["impersonates"] = brand
            result["signals"].append(f"Uses the name '{brand}' but is not an official {brand} domain")

        registered = _rdap_registration_date(registrable_domain(host))
        if registered:
            age_days = (datetime.now(timezone.utc) - registered).days
            result["domain_age_days"] = age_days
            if age_days < _YOUNG_DOMAIN_DAYS:
                result["signals"].append(f"Domain registered only {age_days} days ago")

        blocklisted = [name for name, hit in (("Google Safe Browsing", _safe_browsing_hit(url)), ("URLhaus", _urlhaus_hit(host))) if hit]
        if blocklisted:
            result["signals"].append(f"Listed as malicious by {', '.join(blocklisted)}")
            result["verdict"] = "malicious"
        elif brand or result.get("domain_age_days", 10**6) < _YOUNG_DOMAIN_DAYS:
            result["verdict"] = "suspicious"

    _cache[host] = (time.time(), result)
    return result


def check_urls_in_text(text: str) -> list[dict]:
    urls = extract_entities(text).get("url", [])[:_MAX_URLS]
    if not urls:
        return []
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(urls)) as pool:
        return list(pool.map(check_url, urls))


def risk_floor(checks: list[dict]) -> tuple[int, str] | None:
    """Minimum (risk_score, verdict) implied by hard evidence, or None."""
    if any(c["verdict"] == "malicious" for c in checks):
        return 90, "SCAM"
    young_lookalike = any(c.get("impersonates") and c.get("domain_age_days", 10**6) < _YOUNG_DOMAIN_DAYS for c in checks)
    if young_lookalike:
        return 85, "SCAM"
    if any(c.get("impersonates") for c in checks):
        return 70, "SUSPICIOUS"
    return None
