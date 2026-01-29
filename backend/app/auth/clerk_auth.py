import os
import httpx
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, jwk
from jose.utils import base64url_decode
from dotenv import load_dotenv

load_dotenv()

CLERK_ISSUER_URL = os.getenv("CLERK_ISSUER_URL") # e.g. https://<your-instance>.clerk.accounts.dev
# Alternatively, fetch JWKS from https://api.clerk.com/v1/jwks or the issuer endpoint

security = HTTPBearer()

jwks_cache = None

async def get_jwks():
    global jwks_cache
    if jwks_cache:
        return jwks_cache
    
    # Normally you'd get this from your Clerk Dashboard -> API Keys -> JWKS URL
    # Or construct it: https://<your-clerk-domain>/.well-known/jwks.json
    jwks_url = os.getenv("CLERK_JWKS_URL")
    if not jwks_url:
        raise HTTPException(status_code=500, detail="CLERK_JWKS_URL not set")

    async with httpx.AsyncClient() as client:
        response = await client.get(jwks_url)
        jwks_cache = response.json()
    return jwks_cache

async def verify_clerk_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    
    try:
        # 1. Get Key ID from Header
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        
        # 2. Get Public Key from JWKS
        jwks = await get_jwks()
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)
        
        if not key:
            raise HTTPException(status_code=401, detail="Invalid token key ID")

        # 3. Verify Token
        public_key = jwk.construct(key)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="cyberguard-backend", # Optional: Set if you configured audience in Clerk
            options={"verify_aud": False}  # Disable aud check if not configured
        )
        
        return payload # Contains 'sub' (user_id), 'email', etc.
        
    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

def get_current_user(payload: dict = Security(verify_clerk_token)):
    return payload.get("sub") # The Clerk User ID
