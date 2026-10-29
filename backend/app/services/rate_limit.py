"""
Tiny in-memory sliding-window rate limiter.

Good enough for a single Render instance (state resets on restart, which is fine): its job is to stop
one caller from draining the free Groq/Gemini quotas, not to be a distributed limiter.
"""
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request

_MAX_TRACKED_KEYS = 10_000
_hits: dict[str, deque] = defaultdict(deque)


def client_ip(request: Request) -> str:
    # Render (and most PaaS) put the real client first in X-Forwarded-For.
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(name: str, limit: int, window_seconds: int):
    """FastAPI dependency: at most `limit` calls per `window_seconds` per client IP for this route group."""

    async def dependency(request: Request) -> None:  # async so it runs on the event loop (no thread races)
        now = time.monotonic()
        key = f"{name}:{client_ip(request)}"
        hits = _hits[key]
        while hits and now - hits[0] > window_seconds:
            hits.popleft()
        if len(hits) >= limit:
            retry_after = int(window_seconds - (now - hits[0])) + 1
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Please try again in {retry_after} seconds.",
                headers={"Retry-After": str(retry_after)},
            )
        hits.append(now)
        if len(_hits) > _MAX_TRACKED_KEYS:
            for stale in [k for k, v in _hits.items() if not v or now - v[-1] > 3600]:
                _hits.pop(stale, None)

    return dependency


# Shared limits for LLM-backed endpoints (tune via code; they are per IP).
llm_heavy = rate_limit("llm_heavy", limit=10, window_seconds=60 * 10)   # full multi-agent runs
llm_light = rate_limit("llm_light", limit=30, window_seconds=60 * 10)   # single LLM call endpoints
read_only = rate_limit("read_only", limit=120, window_seconds=60)
