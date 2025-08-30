import os
from dotenv import load_dotenv
import asyncpg
import asyncio

# Load environment variables
load_dotenv('env_config.txt')
DATABASE_URL = os.getenv('DATABASE_URL')

# Convert SQLAlchemy URL to asyncpg format
def convert_to_asyncpg_url(sqlalchemy_url):
    url = sqlalchemy_url.replace('postgresql+asyncpg://', 'postgresql://')
    return url

async def fix_schema():
    try:
        asyncpg_url = convert_to_asyncpg_url(DATABASE_URL)
        print(f"Connecting with URL: {asyncpg_url}")
        conn = await asyncpg.connect(asyncpg_url)

        print("Current categories table schema:")
        result = await conn.fetch("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'categories'
            ORDER BY ordinal_position
        """)
        for row in result:
            print(f"Column: {row['column_name']}, Type: {row['data_type']}, Default: {row['column_default']}, Nullable: {row['is_nullable']}")

        print("\nFixing categories table schema...")
        # Create sequence
        await conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS categories_id_seq OWNED BY categories.id;
        """)
        # Set default to nextval of sequence
        await conn.execute("""
            ALTER TABLE categories ALTER COLUMN id SET DEFAULT nextval('categories_id_seq');
        """)
        # Set sequence current value to max id
        await conn.execute("""
            SELECT setval('categories_id_seq', COALESCE((SELECT MAX(id) FROM categories), 1), false);
        """)

        print("Categories schema fixed successfully!")

        print("\nFixing words table schema...")
        # Create sequence for words table
        await conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS words_id_seq OWNED BY words.id;
        """)
        # Set default to nextval of sequence
        await conn.execute("""
            ALTER TABLE words ALTER COLUMN id SET DEFAULT nextval('words_id_seq');
        """)
        # Set sequence current value to max id
        await conn.execute("""
            SELECT setval('words_id_seq', COALESCE((SELECT MAX(id) FROM words), 1), false);
        """)

        print("Words schema fixed successfully!")

        print("\nFixed categories table schema:")
        result = await conn.fetch("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'categories'
            ORDER BY ordinal_position
        """)
        for row in result:
            print(f"Column: {row['column_name']}, Type: {row['data_type']}, Default: {row['column_default']}, Nullable: {row['is_nullable']}")

        print("\nFixed words table schema:")
        result = await conn.fetch("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'words'
            ORDER BY ordinal_position
        """)
        for row in result:
            print(f"Column: {row['column_name']}, Type: {row['data_type']}, Default: {row['column_default']}, Nullable: {row['is_nullable']}")

        await conn.close()

    except Exception as e:
        print(f"Error fixing schema: {e}")

if __name__ == "__main__":
    asyncio.run(fix_schema())
