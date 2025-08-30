# app/db.py

"""Nastavenie databázy pre SQLAlchemy."""

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase

# Load environment variables from env_config.txt
load_dotenv('env_config.txt')

# Použiť environment variable pre databázové pripojenie
# Formát pre Supabase: postgresql+asyncpg://postgres:[password]@[host]:[port]/postgres
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required for PostgreSQL connection")

engine = create_async_engine(DATABASE_URL, echo=False)

async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    """Základná trieda pre modely."""
    pass

async def get_db_session() -> AsyncSession:
    """Dependency pre získanie databázovej session."""
    async with async_session() as session:
        yield session
