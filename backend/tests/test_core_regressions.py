"""Regression tests for bugs found in the October 2026 review. They run offline (no API keys, no DB)."""
import asyncio

import pytest
from fastapi.testclient import TestClient


def test_resolve_graph_runs_without_thread_id(monkeypatch):
    """The graph used to be compiled with a checkpointer and crashed on every invoke without a thread_id."""
    import app.workflows.cyber_resolve_graph as graph
    from app.schemas.resolution import IncidentRequest

    monkeypatch.setattr(graph, "search_incident_info", lambda *a, **k: "")
    case_state, _guide = asyncio.run(graph.run_resolution(IncidentRequest(description="Someone took Rs 5000 via pay.refund8821@ybl")))

    assert case_state.strategy.lifecycle_plan, "falls back to the curated playbook when the LLM is unavailable"
    labels = [n["label"] for n in case_state.graph_data["nodes"]]
    assert "pay.refund8821@ybl" in labels, "graph contains real indicators from the description"


def test_scam_detection_fails_closed():
    """When analysis breaks, the verdict must never be SAFE."""
    from app.agents.scam_detection_agent import detect_scam
    from app.schemas.common import UserProfile

    report = detect_scam("Your KYC expired, click bit.ly/x", UserProfile(user_type="adult"))
    assert report.analysis_status == "failed"
    assert report.verdict != "SAFE"
    assert report.risk_score >= 50


def test_entity_extraction_finds_bare_domains_and_upi():
    from app.services.entity_extraction import extract_entities

    found = extract_entities("Pay pay.refund8821@ybl, visit gpay-refund-portal.xyz/claim or https://sbi-netbanking.co/login. Call +91 9876543210")
    assert found["upi_id"] == ["pay.refund8821@ybl"]
    assert set(found["url"]) == {"gpay-refund-portal.xyz/claim", "https://sbi-netbanking.co/login"}
    assert found["phone_number"] == ["9876543210"]


def test_scam_knowledge_is_deterministic_and_relevant():
    from app.services.scam_knowledge import search_scam_patterns

    first = search_scam_patterns("Congratulations you won KBC lottery of 25 lakh")
    assert first and "KBC" in first[0]
    assert first == search_scam_patterns("Congratulations you won KBC lottery of 25 lakh")
    assert search_scam_patterns("hello how are you") == []


def test_pdf_handles_non_latin_text():
    from app.routers.reports import _latin1, _ReportPDF

    pdf = _ReportPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)
    pdf.para(_latin1("Lost ₹5,000 — scammer said “urgent” हिंदी"))
    assert bytes(pdf.output()).startswith(b"%PDF")


def test_risk_score_needs_independent_reporters():
    from app.services.memory_service import CONFIRMATION_THRESHOLD, ThreatMemoryService

    assert ThreatMemoryService._compute_risk_score(1) < ThreatMemoryService._compute_risk_score(CONFIRMATION_THRESHOLD)
    assert ThreatMemoryService._compute_risk_score(100) <= 0.95


def test_public_endpoints_validate_and_rate_limit():
    from app.main import app

    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"
    assert client.post("/analyze-message", json={"message": "   "}).status_code == 400
    assert client.post("/analyze-message", json={"message": "x" * 9000}).status_code == 422

    # Auth-only endpoints reject anonymous callers.
    assert client.post("/api/investigate", json={"message": "hi", "sessionId": "s1"}).status_code in (401, 403)
    assert client.get("/cases").status_code in (401, 403)

    statuses = [client.post("/case/doubt", json={"question": ""}).status_code for _ in range(35)]
    assert 429 in statuses, "light LLM endpoints are rate limited per IP"
