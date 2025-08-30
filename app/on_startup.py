# app/on_startup.py
from app.db import engine, Base

async def create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def on_startup() -> None:
    await create_tables()
