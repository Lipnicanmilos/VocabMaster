# init_db.py

"""Jednorazová inicializácia databázy."""

import asyncio
from app.db import engine
from app.models import Base

async def create_db_and_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(create_db_and_tables())
