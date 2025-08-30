import asyncio
from app.db import async_session
from app.models import User
from app.auth.service import hash_password

async def test_save_user():
    async with async_session() as session:
        new_user = User(email="testuser@example.com", hashed_password=hash_password("testpassword"))
        session.add(new_user)
        await session.commit()
        print("User saved successfully")

if __name__ == "__main__":
    asyncio.run(test_save_user())
