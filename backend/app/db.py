from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


def _database_url() -> str:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is required.")
    return DATABASE_URL


engine = create_engine(_database_url(), pool_pre_ping=True) if DATABASE_URL else None
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False) if engine else None


def ensure_database_schema() -> None:
    if engine is None:
        return
    from app.models import User  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL is required.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
