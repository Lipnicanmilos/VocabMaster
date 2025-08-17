# app/db.py

"""Nastavenie databázy pre SQLAlchemy."""

from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = "sqlite+aiosqlite:///./vocab.db"

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """Základná trieda pre modely."""
    pass

async def get_db_session() -> AsyncSession:
    """Dependency pre získanie databázovej session."""
    async with async_session() as session:
        yield session
