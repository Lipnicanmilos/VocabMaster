import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import asyncio

# Load environment variables
load_dotenv('env_config.txt')
DATABASE_URL = os.getenv('DATABASE_URL')

async def test_connection():
    try:
        print(f"Testing connection to: {DATABASE_URL}")
        
        # Create async engine
        engine = create_async_engine(DATABASE_URL, echo=True)
        
        # Test connection
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"PostgreSQL version: {version}")
            
            # Test if we can insert into categories
            try:
                await conn.execute(text("""
                    INSERT INTO categories (name, user_id) 
                    VALUES ('Test Category', 1)
                    RETURNING id
                """))
                print("✅ Successfully inserted test category!")
            except Exception as e:
                print(f"❌ Error inserting category: {e}")
                
            # Count existing categories
            result = await conn.execute(text("SELECT COUNT(*) FROM categories"))
            count = result.scalar()
            print(f"Total categories in database: {count}")
            
            # Count existing words
            result = await conn.execute(text("SELECT COUNT(*) FROM words"))
            count = result.scalar()
            print(f"Total words in database: {count}")
            
        await engine.dispose()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if success:
        print("\n✅ Database connection test PASSED")
    else:
        print("\n❌ Database connection test FAILED")
