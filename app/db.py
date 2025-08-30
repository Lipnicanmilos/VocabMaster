# app/db.py

"""Nastavenie databázy pre SQLAlchemy."""

import os
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

# Použiť environment variable pre databázové pripojenie
# Formát pre Supabase: postgresql+asyncpg://postgres:[password]@[host]:[port]/postgres
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "sqlite+aiosqlite:///./vocab.db"  # fallback na SQLite
)

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """Základná trieda pre modely."""
    pass

async def get_db_session() -> AsyncSession:
    """Dependency pre získanie databázovej session."""
    async with async_session() as session:
        yield session
