from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from app.db.mongodb import get_db
from app.services.memory_service import ThreatMemoryService
from app.services.official_sources import BRAND_KEYWORDS, OFFICIAL_DOMAINS, domain_of
from app.services.rate_limit import rate_limit
from app.services.url_intel import check_url

router = APIRouter(prefix="/api", tags=["URL check"])

url_check_limit = rate_limit("url_check", limit=60, window_seconds=600)


class UrlCheckRequest(BaseModel):
    url: str = Field(..., min_length=3, max_length=2000)


@router.post("/url-check", dependencies=[Depends(url_check_limit)])
async def url_check(req: UrlCheckRequest, db=Depends(get_db)):
    """Domain age, look-alike and blocklist checks for one URL, plus whether CyberGuard users reported it."""
    result = await run_in_threadpool(check_url, req.url)
    if db is not None:
        known = await ThreatMemoryService(db).check_entities({"url": [req.url, domain_of(req.url)]})
        result["reported_by_users"] = known[0] if known else None
        if known and known[0]["is_confirmed_threat"] and result["verdict"] != "malicious":
            result["verdict"] = "malicious"
            result["signals"].append("Confirmed by multiple CyberGuard user reports")
    return result


@router.get("/official-domains")
async def official_domains():
    """Lets clients (e.g. the browser extension) pre-filter locally, so ordinary browsing is never sent to us."""
    return {"official": OFFICIAL_DOMAINS, "brand_keywords": BRAND_KEYWORDS, "always_official_suffixes": [".gov.in", ".nic.in", ".bank.in"]}
