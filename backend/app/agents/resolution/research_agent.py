"""
Open-web research for a scam/incident query.

Uses DuckDuckGo (free, no key) for web, news and Reddit/X site searches, and returns the raw
snippets. No LLM calls happen here: the downstream agent that consumes the findings already
reasons over them, so a separate "synthesis" call would only burn free-tier quota.
"""
import concurrent.futures
import logging
import time

from app.services.resilience import with_retry_and_circuit_breaker

try:
    from ddgs import DDGS
except ImportError:  # older package name
    from duckduckgo_search import DDGS

logger = logging.getLogger(__name__)

_SEARCH_TIMEOUT_SECONDS = 8    # per search request
_RESEARCH_BUDGET_SECONDS = 12  # whole research step
_CACHE_TTL_SECONDS = 6 * 60 * 60
_MAX_CACHE_ENTRIES = 200
_cache: dict[str, tuple[float, str]] = {}


def search_incident_info(query: str, context: dict | None = None) -> str:
    key = query.strip().lower()
    cached = _cache.get(key)
    if cached and time.time() - cached[0] < _CACHE_TTL_SECONDS:
        return cached[1]

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
    futures = {
        "WEB": executor.submit(perform_web_search, query),
        "NEWS": executor.submit(perform_news_search, query),
        "REDDIT": executor.submit(perform_site_search, query, "reddit.com"),
        "X/TWITTER": executor.submit(perform_site_search, query, "x.com"),
    }
    # Slow sources are skipped rather than waited for; their threads finish in the background.
    concurrent.futures.wait(futures.values(), timeout=_RESEARCH_BUDGET_SECONDS)
    executor.shutdown(wait=False, cancel_futures=True)
    sections = [
        f"=== {name} ===\n{future.result() if future.done() else 'Timed out.'}"
        for name, future in futures.items()
    ]

    findings = "\n\n".join(sections)[:6000]
    if len(_cache) >= _MAX_CACHE_ENTRIES:
        _cache.pop(next(iter(_cache)))
    _cache[key] = (time.time(), findings)
    return findings


def _search(kind: str, query: str, max_results: int) -> list[dict]:
    """ddgs raises on an empty result set; that is a normal outcome, not an outage, so it must not trip the breaker."""
    with DDGS(timeout=_SEARCH_TIMEOUT_SECONDS) as ddgs:
        try:
            return list(getattr(ddgs, kind)(query, max_results=max_results))
        except Exception as e:
            if "no results" in str(e).lower():
                return []
            raise


@with_retry_and_circuit_breaker("DuckDuckGo_Web", max_retries=1)
def perform_web_search(query: str) -> str:
    results = [f"- {r['title']}: {r['body']} ({r['href']})" for r in _search("text", f"{query} scam fraud", 5)]
    return "\n".join(results) or "No web results."


@with_retry_and_circuit_breaker("DuckDuckGo_News", max_retries=1)
def perform_news_search(query: str) -> str:
    results = [f"- {r['title']} ({r.get('source', '')}): {r['body']} ({r['url']})" for r in _search("news", query, 5)]
    return "\n".join(results) or "No recent news."


@with_retry_and_circuit_breaker("DuckDuckGo_Social", max_retries=1)
def perform_site_search(query: str, domain: str) -> str:
    results = [f"- {r['title']}: {r['body']} ({r['href']})" for r in _search("text", f"site:{domain} {query} scam", 4)]
    return "\n".join(results) or f"No results on {domain}."
