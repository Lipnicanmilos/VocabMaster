@echo off
echo Aktualizujem Litestar a súvisiace závislosti na najnovšie verzie...
pip install --upgrade litestar sqlalchemy asyncpg aiosqlite passlib python-jose pydantic pytest pytest-asyncio httpx bcrypt
echo Závislosti boli aktualizované. Prosím, reštartujte aplikáciu a otestujte flash správy.
