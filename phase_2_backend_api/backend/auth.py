"""
Auth utilities: password hashing, JWT creation/verification, in-memory user store.
Seeded with demo@example.com / password123
"""

from __future__ import annotations
import os
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

SECRET_KEY = os.getenv("JWT_SECRET", "zomato-recommender-secret-key-change-in-prod")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 hours

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── In-memory user store {email: hashed_password} ─────────────────────────────
_users: dict[str, str] = {}


def _seed_demo_user() -> None:
    _users["demo@example.com"] = pwd_context.hash("password123")

_seed_demo_user()


# ── Helpers ────────────────────────────────────────────────────────────────────

def get_user(email: str) -> Optional[str]:
    """Return hashed password or None."""
    return _users.get(email.lower().strip())


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def authenticate_user(email: str, password: str) -> bool:
    hashed = get_user(email)
    if hashed is None:
        return False
    return verify_password(password, hashed)


def register_user(email: str, password: str) -> bool:
    """Returns False if email already exists."""
    email = email.lower().strip()
    if email in _users:
        return False
    _users[email] = hash_password(password)
    return True


def create_access_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": email, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    """Returns email from token or None if invalid/expired."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
