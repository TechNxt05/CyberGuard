import logging
import os
import time

import httpx
from dotenv import load_dotenv
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwk, jwt

load_dotenv()

logger = logging.getLogger(__name__)

# e.g. https://<your-instance>.clerk.accounts.dev  (Clerk Dashboard -> API Keys -> Frontend API URL)
CLERK_ISSUER_URL = (os.getenv("CLERK_ISSUER_URL") or "").rstrip("/")
CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL") or (f"{CLERK_ISSUER_URL}/.well-known/jwks.json" if CLERK_ISSUER_URL else "")
# Comma-separated frontend origins allowed to mint tokens, e.g. https://your-app.vercel.app,http://localhost:3000
AUTHORIZED_PARTIES = {p.strip().rstrip("/") for p in os.getenv("CLERK_AUTHORIZED_PARTIES", "").split(",") if p.strip()}

security = HTTPBearer()
optional_security = HTTPBearer(auto_error=False)

_JWKS_MIN_REFRESH_SECONDS = 300
_jwks_cache: dict = {"keys": None, "fetched_at": 0.0}


async def _fetch_jwks() -> list:
    if not CLERK_JWKS_URL:
        raise HTTPException(status_code=500, detail="Authentication is not configured on the server.")
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.get(CLERK_JWKS_URL)
        response.raise_for_status()
    _jwks_cache["keys"] = response.json()["keys"]
    _jwks_cache["fetched_at"] = time.time()
    return _jwks_cache["keys"]


async def _get_signing_key(kid: str) -> dict | None:
    keys = _jwks_cache["keys"] or await _fetch_jwks()
    key = next((k for k in keys if k.get("kid") == kid), None)
    # Unknown kid: Clerk may have rotated keys, so refresh (rate-limited to avoid hammering on bad tokens).
    if key is None and time.time() - _jwks_cache["fetched_at"] > _JWKS_MIN_REFRESH_SECONDS:
        keys = await _fetch_jwks()
        key = next((k for k in keys if k.get("kid") == kid), None)
    return key


async def _verify(token: str) -> dict:
    try:
        key = await _get_signing_key(jwt.get_unverified_header(token).get("kid"))
        if not key:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        payload = jwt.decode(
            token,
            jwk.construct(key),
            algorithms=["RS256"],
            issuer=CLERK_ISSUER_URL or None,
            options={"verify_aud": False, "verify_iss": bool(CLERK_ISSUER_URL)},
        )
        if AUTHORIZED_PARTIES and payload.get("azp", "").rstrip("/") not in AUTHORIZED_PARTIES:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.info("Token rejected: %s", e)
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")


async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    return await _verify(credentials.credentials)


def get_current_user(payload: dict = Security(verify_clerk_token)) -> str:
    return payload.get("sub")


async def get_optional_user(credentials: HTTPAuthorizationCredentials | None = Security(optional_security)) -> str | None:
    """User id when a valid token is sent, None for anonymous callers (invalid tokens are still rejected)."""
    if credentials is None:
        return None
    return (await _verify(credentials.credentials)).get("sub")
