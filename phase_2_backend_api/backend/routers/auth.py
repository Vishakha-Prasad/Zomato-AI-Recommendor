"""
Auth router: /auth/login, /auth/register, /auth/me
"""

from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from phase_2_backend_api.backend.auth import (
    authenticate_user,
    register_user,
    create_access_token,
    decode_token,
)
from phase_2_backend_api.backend.models import UserIn, UserOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    email = decode_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return email


@router.post("/login", response_model=Token)
def login(user: UserIn):
    if not authenticate_user(user.email, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    token = create_access_token(user.email.lower().strip())
    return Token(access_token=token)


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
def register(user: UserIn):
    if not register_user(user.email, user.password):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )
    token = create_access_token(user.email.lower().strip())
    return Token(access_token=token)


@router.get("/me", response_model=UserOut)
def me(email: str = Depends(get_current_user)):
    return UserOut(email=email)
