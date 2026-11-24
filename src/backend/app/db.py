"""SQLAlchemy metadata and environment-driven database engine helpers."""

from __future__ import annotations

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base for persistence models."""


def get_database_url() -> str:
    """Return an explicit database URL; fail clearly when not configured."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured")
    return database_url


def make_engine(database_url: str | None = None) -> Engine:
    """Create an engine only when a caller explicitly requests one."""
    return create_engine(database_url or get_database_url(), pool_pre_ping=True)


def make_session_factory(engine: Engine | None = None) -> sessionmaker[Session]:
    """Create a session factory without connecting until a session is used."""
    selected_engine = engine or make_engine()
    return sessionmaker(bind=selected_engine, expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    """FastAPI dependency for future database-backed routes."""
    factory = make_session_factory()
    with factory() as session:
        yield session
