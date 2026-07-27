from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Literal

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_SECRET_KEY,
    REFRESH_TOKEN_EXPIRE_DAYS,
    RESET_TOKEN_EXPIRE_MINUTES,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return pwd_context.verify(password, password_hash)


def create_token(subject: str, token_type: Literal["access", "refresh", "reset"], expires_delta: timedelta) -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError("JWT_SECRET_KEY is required.")
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(subject: str, remember_me: bool = False) -> str:
    minutes = ACCESS_TOKEN_EXPIRE_MINUTES * (7 if remember_me else 1)
    return create_token(subject, "access", timedelta(minutes=minutes))


def create_refresh_token(subject: str, remember_me: bool = False) -> str:
    days = REFRESH_TOKEN_EXPIRE_DAYS if remember_me else 1
    return create_token(subject, "refresh", timedelta(days=days))


def create_reset_token(subject: str) -> str:
    return create_token(subject, "reset", timedelta(minutes=RESET_TOKEN_EXPIRE_MINUTES))


def decode_token(token: str, expected_type: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid or expired token.") from exc
    if payload.get("type") != expected_type:
        raise ValueError("Invalid token type.")
    subject = payload.get("sub")
    if not subject:
        raise ValueError("Invalid token subject.")
    return str(subject)
