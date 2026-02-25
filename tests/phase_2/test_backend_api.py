"""
Unit tests for FastAPI endpoints using TestClient.
Uses pytest + httpx TestClient. Requires data/zomato_cleaned.csv for restaurant routes.
"""

import pytest
from fastapi.testclient import TestClient

from phase_2_backend_api.backend.main import app

client = TestClient(app)


# ── Health ────────────────────────────────────────────────────────────────────

def test_health():
    """GET /health should return 200 and status ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data.get("status") == "ok"


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_auth_login_success():
    """POST /auth/login with demo credentials should return token."""
    resp = client.post("/auth/login", json={
        "email": "demo@example.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_auth_login_wrong_password():
    """POST /auth/login with wrong password should return 401."""
    resp = client.post("/auth/login", json={
        "email": "demo@example.com",
        "password": "wrong",
    })
    assert resp.status_code == 401


def test_auth_login_invalid_email():
    """POST /auth/login with unknown email should return 401."""
    resp = client.post("/auth/login", json={
        "email": "unknown@example.com",
        "password": "password123",
    })
    assert resp.status_code == 401


def test_auth_register_then_login():
    """Register new user then login should work."""
    email = "newtest@example.com"
    password = "testpass123"
    resp_register = client.post("/auth/register", json={"email": email, "password": password})
    assert resp_register.status_code == 201
    token = resp_register.json()["access_token"]

    resp_me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp_me.status_code == 200
    assert resp_me.json().get("email") == email


def test_auth_me_requires_token():
    """GET /auth/me without token should return 403."""
    resp = client.get("/auth/me")
    assert resp.status_code in (401, 403)


def test_auth_me_invalid_token():
    """GET /auth/me with invalid token should return 401."""
    resp = client.get("/auth/me", headers={"Authorization": "Bearer invalid-token"})
    assert resp.status_code == 401


# ── Restaurant routes (require auth + data file) ───────────────────────────────

def _get_token():
    """Get valid token for protected routes."""
    resp = client.post("/auth/login", json={
        "email": "demo@example.com",
        "password": "password123",
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.mark.skipif(
    not (__import__("pathlib").Path(__file__).resolve().parent.parent / "data" / "zomato_cleaned.csv").exists(),
    reason="data/zomato_cleaned.csv not found"
)
class TestRestaurantEndpoints:
    """Tests for restaurant endpoints (require data file)."""

    def test_restaurants_locations_requires_auth(self):
        """GET /restaurants/locations without auth should return 401."""
        resp = client.get("/restaurants/locations")
        assert resp.status_code in (401, 403)

    def test_restaurants_locations_with_auth(self):
        """GET /restaurants/locations with valid token should return list."""
        token = _get_token()
        resp = client.get("/restaurants/locations", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert all(isinstance(x, str) for x in data)

    def test_restaurants_cuisines_with_auth(self):
        """GET /restaurants/cuisines with valid token should return list."""
        token = _get_token()
        resp = client.get("/restaurants/cuisines", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert all(isinstance(x, str) for x in data)

    def test_recommendations_with_auth(self):
        """POST /recommendations with valid payload should return list."""
        token = _get_token()
        resp = client.post(
            "/recommendations",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"location": "", "cuisines": [], "min_rating": 0.0, "max_price": None},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
