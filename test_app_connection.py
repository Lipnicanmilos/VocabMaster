#!/usr/bin/env python3
"""
Skript na testovanie pripojenia aplikácie k Supabase.
"""

import asyncio
import os
from app.db import engine

async def test_app_connection():
    """Testuje, či aplikácia môže pripojiť k Supabase."""
    try:
        async with engine.connect():
            print("✅ Aplikácia úspešne pripojená k Supabase")
            return True
    except Exception as e:
        print(f"❌ Chyba pri pripájaní aplikácie: {e}")
        return False

if __name__ == "__main__":
    # Načítaj env_config.txt
    try:
        from dotenv import load_dotenv
        load_dotenv("env_config.txt")
        print("📁 Načítavam env_config.txt súbor")
    except ImportError:
        print("ℹ️  python-dotenv nie je nainštalovaný, používam system environment")
    
    asyncio.run(test_app_connection())
