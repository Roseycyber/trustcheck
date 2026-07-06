"""
API-level tests.

Unlike test_risk_engine.py and test_safe_verify.py, these require the
project's actual dependencies (FastAPI, Pydantic, httpx) installed:

    pip install -r requirements-dev.txt
    pytest

They exist to catch wiring/serialization mistakes in main.py; the
behavioural logic itself is already covered, without any dependencies,
in test_risk_engine.py and test_safe_verify.py.
"""

try:
    import pytest
except ImportError:  # pragma: no cover - lets `python -m unittest discover` skip cleanly
    pytest = None

if pytest is not None:
    fastapi_testclient = pytest.importorskip("fastapi.testclient")
    from app.main import app  # noqa: E402

    client = fastapi_testclient.TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_check_endpoint_returns_expected_shape():
    response = client.post(
        "/api/check",
        json={
            "content": "URGENT: pay a registration fee via gift card immediately",
            "category": "job",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["verdict"] in {"verify", "suspicious", "high_risk"}
    assert "safe" not in body["verdict_label"].lower()
    assert len(body["reasons"]) <= 2
    assert "heading" in body["safe_verify"]
    assert "disclaimer" in body["safe_verify"]


def test_check_endpoint_defaults_category_to_other():
    response = client.post("/api/check", json={"content": "Hello, just checking in."})
    assert response.status_code == 200


def test_check_endpoint_rejects_empty_content():
    response = client.post("/api/check", json={"content": ""})
    assert response.status_code == 422


def test_check_endpoint_rejects_invalid_category():
    response = client.post(
        "/api/check", json={"content": "hello", "category": "not-a-real-category"}
    )
    assert response.status_code == 422
