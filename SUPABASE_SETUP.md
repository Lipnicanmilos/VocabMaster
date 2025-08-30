# Nastavenie Supabase pre VocabMaster

Tento návod vysvetľuje ako prepojiť Vašu aplikáciu VocabMaster so Supabase databázou.

## 📋 Predpoklady

- Máte vytvorený Supabase projekt a tabuľky
- Python 3.8+ nainštalovaný
- Balíčky z `requirements.txt` nainštalované

## 🔧 Krok 1: Získanie connection stringu z Supabase

1. Otvorte Váš Supabase projekt v prehliadači
2. Prejdite do **Settings** → **Database**
3. V sekcii **Connection string** vyberte **URI**
4. Skopírujte connection string, ktorý vyzerá podobne ako:
   ```
   postgresql://postgres:[password]@[host]:[port]/postgres
   ```

## 🛠️ Krok 2: Nastavenie environment variables

1. Vytvorte súbor `.env` v koreňovom adresári projektu:
   ```bash
   cp .env.example .env
   ```

2. Upravte súbor `.env` a nahraďte placeholder hodnoty:
   ```env
   DATABASE_URL=postgresql+asyncpg://postgres:VAŠE_HESLO@VAŠ_HOST:5432/postgres
   ```

   **Dôležité:** Pridajte `+asyncpg` za `postgresql` aby ste použili async driver!

## 🧪 Krok 3: Testovanie pripojenia

Spustite testovací skript na overenie pripojenia:

```bash
python test_supabase_connection.py
```

Ak všetko funguje, uvidíte:
- ✅ Úspešné pripojenie k PostgreSQL
- 📊 Zoznam existujúcich tabuliek
- ✅ Potvrdenie, že požadované tabuľky existujú

## 📊 Krok 4: Kontrola štruktúry tabuliek

Ak chcete skontrolovať, či Vaše tabuľky v Supabase majú správnu štruktúru:

1. Otvorte SQL editor v Supabase
2. Skopírujte a spustite obsah súboru `supabase_schema_check.sql`
3. Skontrolujte, či štruktúra zodpovedá očakávanej (popísanej v komentároch)

## 🚀 Krok 5: Spustenie aplikácie

Teraz môžete spustiť aplikáciu, ktorá bude používať Supabase:

```bash
# Ak používate uvicorn priamo
uvicorn app.main:app --reload

# Alebo podľa Vášho spôsobu spúšťania
```

## 🔍 Riešenie problémov

### Chyba: "password authentication failed"
- Skontrolujte heslo v connection stringu
- Overte, či máte prístup k databáze v Supabase

### Chyba: "connection timeout"
- Skontrolujte hostname a port v connection stringu
- Overte, či je databáza prístupná z Vášho IP (možno treba povoliť v Supabase settings)

### Tabuľky neexistujú
Ak tabuľky `users`, `categories`, `words` neexistujú, môžete ich vytvoriť pomocou tohto SQL:

```sql
-- Vytvorenie tabuliek podľa SQLAlchemy modelov
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    user_id INTEGER REFERENCES users(id)
);

CREATE TABLE words (
    id SERIAL PRIMARY KEY,
    sk VARCHAR NOT NULL,
    en VARCHAR NOT NULL,
    level INTEGER DEFAULT 1,
    category_id INTEGER REFERENCES categories(id)
);

-- Vytvorenie indexov
CREATE INDEX idx_users_email ON users(email);
```

## 🌐 Environment Variables

| Premenná | Popis | Príklad |
|----------|-------|---------|
| `DATABASE_URL` | Connection string k Supabase | `postgresql+asyncpg://postgres:pass@host:5432/postgres` |
| `SQL_ECHO` | Logovanie SQL dotazov (voliteľné) | `false` |

## 📞 Podpora

Ak máte problémy s pripojením:
1. Skontrolujte Supabase dashboard → Settings → Database
2. Overte, že máte správne heslo a hostname
3. Skontrolujte, či máte povolený prístup z Vášho IP adresy
