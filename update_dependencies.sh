@echo off
echo Updating Litestar and related dependencies to latest versions...
pip install --upgrade litestar sqlalchemy asyncpg aiosqlite passlib python-jose pydantic pytest pytest-asyncio httpx bcrypt
echo Dependencies updated. Please restart your application and test flash messages again.
