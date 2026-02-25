"""
Unit tests for backend.auth: password hashing, JWT, user registration/login.
Uses pytest (see requirements.txt).
"""

import pytest
from backend.auth import (
    authenticate_user,
    register_user,
    create_access_token,
    decode_token,
    verify_password,
    hash_password,
)


# ── Authentication ────────────────────────────────────────────────────────────

def test_demo_user_can_login():
    """Demo user demo@example.com / password123 should authenticate."""
    assert authenticate_user("demo@example.com", "password123") is True


def test_demo_user_wrong_password():
    """Wrong password should fail."""
    assert authenticate_user("demo@example.com", "wrong") is False


def test_nonexistent_user():
    """Unknown email should fail."""
    assert authenticate_user("unknown@example.com", "password") is False


def test_authenticate_case_insensitive_email():
    """Email lookup should be case-insensitive."""
    assert authenticate_user("DEMO@EXAMPLE.COM", "password123") is True


# ── Registration ──────────────────────────────────────────────────────────────

def test_register_new_user():
    """Registering a new user should succeed."""
    ok = register_user("newuser@test.com", "securepass123")
    assert ok is True
    assert authenticate_user("newuser@test.com", "securepass123") is True


def test_register_duplicate_email_returns_false():
    """Registering same email again should return False."""
    register_user("dup@test.com", "pass1")
    ok = register_user("dup@test.com", "pass2")
    assert ok is False
    assert authenticate_user("dup@test.com", "pass1") is True


# ── JWT tokens ─────────────────────────────────────────────────────────────────

def test_create_and_decode_token():
    """Valid token should decode to email."""
    token = create_access_token("user@example.com")
    assert isinstance(token, str)
    email = decode_token(token)
    assert email == "user@example.com"


def test_decode_invalid_token():
    """Invalid token should return None."""
    assert decode_token("invalid-token") is None


def test_decode_empty_token():
    """Empty token should return None."""
    assert decode_token("") is None


# ── Password helpers ───────────────────────────────────────────────────────────

def test_hash_password():
    """hash_password should return non-empty string."""
    h = hash_password("mypassword")
    assert isinstance(h, str)
    assert len(h) > 0


def test_verify_password():
    """verify_password should match hash_password output."""
    plain = "testpass"
    hashed = hash_password(plain)
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong", hashed) is False
