"""Contract tests using in-memory synthetic PDFs; no private manuscripts."""
from io import BytesIO

import fitz
from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def pdf_with(text):
    doc = fitz.open()
    page = doc.new_page()
    if text:
        page.insert_text((72, 90), text)
    data = doc.tobytes()
    doc.close()
    return data


def submit(data, name="fixture.pdf"):
    return client.post(
        "/api/v1/analyze",
        files={"file": (name, BytesIO(data), "application/pdf")},
    )


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["schema_version"] == "1.0"


def test_pdf_to_evidence_contract():
    response = submit(pdf_with("Simulations used GROMACS 2024.1 at 300 K and TIP3P."))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["schema_version"] == "1.0"
    assert payload["document"]["pages"] == 1
    assert any(x["field"] == "MD engine" for x in payload["method_candidates"])
    assert all(x["grouping_status"] == "unassigned" for x in payload["method_candidates"])
    assert "NOT auto-grouped" in payload["disclaimer"]


def test_invalid_signature_rejected():
    response = submit(b"definitely not a PDF")
    assert response.status_code == 422


def test_unknown_file_extension_rejected():
    assert submit(pdf_with("GROMACS"), "test.txt").status_code == 415


def test_scanned_or_empty_text_pdf_rejected():
    response = submit(pdf_with(""))
    assert response.status_code == 422
    assert "No selectable text" in response.json()["detail"]


def test_no_results_is_valid_and_explicit():
    response = submit(pdf_with("This page describes no simulation methods."))
    assert response.status_code == 200
    assert response.json()["method_candidates"] == []


def test_cors_allows_local_frontend_only():
    response = client.options(
        "/api/v1/analyze",
        headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"


def test_cors_allows_explicit_ipv4_loopback_origin():
    response = client.options(
        "/api/v1/analyze",
        headers={"Origin": "http://127.0.0.1:3000", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") == "http://127.0.0.1:3000"


def test_cors_rejects_untrusted_origin():
    response = client.options(
        "/api/v1/analyze",
        headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"},
    )
    assert response.headers.get("access-control-allow-origin") is None
