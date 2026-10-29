"""
Checks that every official link the app hands to victims still responds.
Run weekly by .github/workflows/link-check.yml; exits 1 if any link looks dead.
"""
import os
import sys

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.authority_directory import VERIFIED_AUTHORITIES  # noqa: E402
from app.services.official_sources import OFFICIAL_DOMAINS  # noqa: E402

HEADERS = {"User-Agent": "Mozilla/5.0 (CyberGuard link checker)"}


def urls() -> set[str]:
    found = {f"https://{domains[0]}" for domains in OFFICIAL_DOMAINS.values()}
    for entry in VERIFIED_AUTHORITIES.values():
        found |= {v for v in entry.values() if isinstance(v, str) and v.startswith("http")}
    return found


def main() -> int:
    failures = []
    with httpx.Client(headers=HEADERS, timeout=20, follow_redirects=True) as client:
        for url in sorted(urls()):
            try:
                try:
                    status = client.get(url).status_code
                except httpx.TransportError:
                    # Some sites only answer on www. (e.g. incometax.gov.in)
                    status = client.get(url.replace("https://", "https://www.", 1)).status_code
                # Many bank/government sites block bots with 403; that still proves the site exists.
                ok = status < 400 or status in (401, 403, 405, 429)
            except Exception as e:
                status, ok = type(e).__name__, False
            print(f"{'OK  ' if ok else 'FAIL'} {status} {url}")
            if not ok:
                failures.append(url)
    if failures:
        print(f"\n{len(failures)} link(s) need attention.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
