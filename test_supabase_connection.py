#!/usr/bin/env python3
"""
Skript na testovanie pripojenia k Supabase databáze.
Spustiť: python test_supabase_connection.py
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

async def test_connection():
    # Načítaj DATABASE_URL z environment variables
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("❌ DATABASE_URL nie je nastavený v environment variables")
        print("Vytvor súbor .env s obsahom:")
        print("DATABASE_URL=postgresql+asyncpg://postgres:[password]@[host]:[port]/postgres")
        return
    
    print(f"🔗 Testujem pripojenie k: {database_url}")
    
    try:
        # Vytvor engine
        engine = create_async_engine(database_url, echo=False)
        
        # Test pripojenia
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"✅ Úspešne pripojené k PostgreSQL: {version}")
            
            # Skontroluj existujúce tabuľky
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            print(f"📊 Existujúce tabuľky: {tables}")
            
            # Skontroluj štruktúru kľúčových tabuliek
            expected_tables = ['users', 'categories', 'words']
            for table in expected_tables:
                if table in tables:
                    print(f"✅ Tabuľka '{table}' existuje")
                else:
                    print(f"⚠️  Tabuľka '{table}' neexistuje")
            
    except Exception as e:
        print(f"❌ Chyba pri pripájaní: {e}")
        print("Skontroluj:")
        print("1. Či je DATABASE_URL správny")
        print("2. Či máš prístup k databáze")
        print("3. Či je databáza spustená")

if __name__ == "__main__":
    # Načítaj env_config.txt file ak existuje (pretože .env je virtual environment)
    try:
        from dotenv import load_dotenv
        load_dotenv("env_config.txt")
        print("📁 Načítavam env_config.txt súbor")
    except ImportError:
        print("ℹ️  python-dotenv nie je nainštalovaný, používam system environment")
    
    asyncio.run(test_connection())
