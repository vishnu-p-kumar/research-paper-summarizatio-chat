from __future__ import annotations

import time
from collections import defaultdict, deque

from sqlalchemy.orm import Session

from app.auth.security import create_reset_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthError(ValueError):
    pass


_login_attempts: dict[str, deque[float]] = defaultdict(deque)


def _check_login_rate_limit(email: str, max_attempts: int = 5, window_s: int = 300) -> None:
    now = time.time()
    attempts = _login_attempts[email]
    while attempts and now - attempts[0] > window_s:
        attempts.popleft()
    if len(attempts) >= max_attempts:
        raise AuthError("Too many login attempts. Please try again in a few minutes.")
    attempts.append(now)


class AuthService:
    def __init__(self, db: Session):
        self.repo = UserRepository(db)

    def register(self, full_name: str, email: str, password: str) -> User:
        if self.repo.get_by_email(email):
            raise AuthError("An account with this email already exists.")
        return self.repo.create(full_name, email, hash_password(password))

    def authenticate(self, email: str, password: str) -> User:
        email_key = email.lower().strip()
        _check_login_rate_limit(email_key)
        user = self.repo.get_by_email(email_key)
        if not user or not verify_password(password, user.password_hash):
            raise AuthError("Invalid email or password.")
        _login_attempts[email_key].clear()
        return user

    def forgot_password(self, email: str) -> str | None:
        user = self.repo.get_by_email(email)
        if not user:
            return None
        return create_reset_token(user.email)

    def reset_password(self, email: str, password: str) -> User:
        user = self.repo.get_by_email(email)
        if not user:
            raise AuthError("Invalid reset token.")
        return self.repo.update_password(user, hash_password(password))
