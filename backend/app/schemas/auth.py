from __future__ import annotations

import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


def validate_strong_password(password: str) -> str:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        raise ValueError("Password must include at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        raise ValueError("Password must include at least one lowercase letter.")
    if not re.search(r"\d", password):
        raise ValueError("Password must include at least one number.")
    if not re.search(r"[^A-Za-z0-9]", password):
        raise ValueError("Password must include at least one special character.")
    return password


class UserOut(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        return validate_strong_password(value)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1)
    remember_me: bool = False


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str = Field(min_length=10)
    password: str

    @field_validator("password")
    @classmethod
    def strong_password(cls, value: str) -> str:
        return validate_strong_password(value)


class MessageResponse(BaseModel):
    message: str


class AuthResponse(BaseModel):
    user: UserOut
    message: str
