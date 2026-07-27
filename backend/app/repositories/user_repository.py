from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower().strip())
        return self.db.execute(stmt).scalar_one_or_none()

    def create(self, full_name: str, email: str, password_hash: str) -> User:
        user = User(
            full_name=full_name.strip(),
            email=email.lower().strip(),
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, password_hash: str) -> User:
        user.password_hash = password_hash
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
