from __future__ import annotations

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.auth.security import create_access_token, create_refresh_token, decode_token
from app.config import COOKIE_SECURE
from app.db import get_db
from app.models.user import User
from app.schemas.auth import (
    AuthResponse,
    ForgotPasswordRequest,
    LoginRequest,
    MessageResponse,
    RegisterRequest,
    ResetPasswordRequest,
    UserOut,
)
from app.services.auth_service import AuthError, AuthService


router = APIRouter(prefix="", tags=["auth"])


def _set_auth_cookies(response: Response, email: str, remember_me: bool) -> str:
    access_token = create_access_token(email, remember_me=remember_me)
    refresh_token = create_refresh_token(email, remember_me=remember_me)
    cookie_args = {
        "httponly": True,
        "secure": COOKIE_SECURE,
        "samesite": "none" if COOKIE_SECURE else "lax",
        "path": "/",
    }
    # No max_age/expires: browser session cookies disappear when the browser session ends.
    response.set_cookie("access_token", access_token, **cookie_args)
    response.set_cookie("refresh_token", refresh_token, **cookie_args)
    return access_token


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        "access_token",
        path="/",
        secure=COOKIE_SECURE,
        samesite="none" if COOKIE_SECURE else "lax",
    )
    response.delete_cookie(
        "refresh_token",
        path="/",
        secure=COOKIE_SECURE,
        samesite="none" if COOKIE_SECURE else "lax",
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).register(payload.full_name, payload.email, payload.password)
    except AuthError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    access_token = _set_auth_cookies(response, user.email, remember_me=False)
    return {"user": user, "message": "Account created successfully.", "access_token": access_token}


@router.post("/login", response_model=AuthResponse)
async def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user = AuthService(db).authenticate(payload.email, payload.password)
    except AuthError as exc:
        status_code = status.HTTP_429_TOO_MANY_REQUESTS if "Too many" in str(exc) else status.HTTP_401_UNAUTHORIZED
        raise HTTPException(status_code=status_code, detail=str(exc)) from exc
    access_token = _set_auth_cookies(response, user.email, remember_me=payload.remember_me)
    return {"user": user, "message": "Logged in successfully.", "access_token": access_token}


@router.post("/logout", response_model=MessageResponse)
async def logout(response: Response):
    _clear_auth_cookies(response)
    return {"message": "Logged out successfully."}


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    token = AuthService(db).forgot_password(payload.email)
    # In production, email this link using an email provider. Returning no token
    # keeps account existence private.
    if token:
        print(f"Password reset token for {payload.email}: {token}")
    return {"message": "If an account exists, reset instructions have been sent."}


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        email = decode_token(payload.token, "reset")
        AuthService(db).reset_password(email, payload.password)
    except (ValueError, AuthError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return {"message": "Password reset successfully. You can now log in."}


@router.get("/me", response_model=UserOut)
async def me(
    response: Response,
    access_token: str | None = Cookie(default=None),
    refresh_token: str | None = Cookie(default=None),
    db: Session = Depends(get_db),
):
    repo = AuthService(db).repo
    email: str | None = None
    if access_token:
        try:
            email = decode_token(access_token, "access")
        except ValueError:
            email = None
    if not email and refresh_token:
        try:
            email = decode_token(refresh_token, "refresh")
            _set_auth_cookies(response, email, remember_me=False)
        except ValueError:
            email = None
    if not email:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    user = repo.get_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User no longer exists.")
    return user
