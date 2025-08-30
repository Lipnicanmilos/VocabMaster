# app/on_startup.py
import os
from dotenv import load_dotenv
from app.db import engine, Base
import logging

# Load environment variables from env_config.txt
load_dotenv('env_config.txt')

logging.info(f"Using DATABASE_URL: {os.getenv('DATABASE_URL')}")

async def create_tables() -> None:
    async with engine.begin() as conn:
        # Drop all tables first to recreate with correct schema
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def on_startup() -> None:
    await create_tables()
