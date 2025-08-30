-- SQL skript na kontrolu štruktúry tabuliek v Supabase
-- Spustiť v SQL editore Supabase

-- 1. Kontrola existencie tabuliek
SELECT 
    table_name,
    CASE 
        WHEN table_name IN ('users', 'categories', 'words') THEN '✅ POŽADOVANÁ'
        ELSE 'ℹ️  VOLITEĽNÁ'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY status, table_name;

-- 2. Detailná štruktúra tabuľky users
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;

-- 3. Detailná štruktúra tabuľky categories  
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'categories' 
ORDER BY ordinal_position;

-- 4. Detailná štruktúra tabuľky words
SELECT 
    column_name, 
    data_type, 
    is_nullable,
    column_default,
    character_maximum_length
FROM information_schema.columns 
WHERE table_name = 'words' 
ORDER BY ordinal_position;

-- 5. Kontrola cudzích kľúčov
SELECT
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name 
FROM 
    information_schema.table_constraints tc 
    JOIN information_schema.key_column_usage kcu ON tc.constraint_name = kcu.constraint_name
    JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
ORDER BY tc.table_name, kcu.column_name;

-- Očakávaná štruktúra podľa SQLAlchemy modelov:
/*
users:
- id: integer (primary key, autoincrement)
- email: varchar(255) (unique, not null, indexed)  
- hashed_password: varchar(255) (not null)
- created_at: timestamp (default current time)

categories:
- id: integer (primary key)
- name: varchar (not null)
- user_id: integer (foreign key to users.id)

words:
- id: integer (primary key)
- sk: varchar (not null) - slovenské slovo
- en: varchar (not null) - anglické slovo  
- level: integer (default 1) - 1: neviem, 2: opakovať, 3: viem
- category_id: integer (foreign key to categories.id)
*/
