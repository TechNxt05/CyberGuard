import os
import sys

import pytest

# Make the `app` package importable when running `pytest` from the backend directory or the repo root.
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Tests never hit real LLMs, search engines, RDAP or blocklists."""
    for key in ("GROQ_API_KEY", "GEMINI_API_KEY", "SERPAPI_API_KEY", "GOOGLE_SAFE_BROWSING_KEY", "URLHAUS_AUTH_KEY"):
        monkeypatch.delenv(key, raising=False)

    from app.services import url_intel
    from app.services.llm_provider import get_llm, get_vision_llm

    monkeypatch.setattr(url_intel, "_rdap_registration_date", lambda domain: None)
    url_intel._cache.clear()
    get_llm.cache_clear()
    get_vision_llm.cache_clear()
    yield
    get_llm.cache_clear()
    get_vision_llm.cache_clear()
