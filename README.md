# VocabMaster

Webová aplikácia na **učenie slovíčok** postavená na **Litestar** (async Python).
Používatelia si vytvárajú kategórie, pridávajú slovíčka (SK/EN) s úrovňami znalosti,
testujú sa a môžu importovať slovíčka z Excelu.

## Funkcie

- Registrácia a prihlásenie používateľov (JWT + bcrypt)
- Kategórie slovíčok viazané na používateľa
- Slovíčka s úrovňami (1 = neviem, 2 = opakovať, 3 = viem)
- Testovací režim
- Import slovíčok z Excelu (openpyxl)
- Server-side session, flash správy

## Technológie

Litestar · SQLAlchemy (async, aiosqlite) · Jinja2 · python-jose (JWT) · passlib/bcrypt · Faker

## Inštalácia

```bash
# 1. Virtuálne prostredie (odporúčaný názov: venv)
python -m venv venv
source venv/Scripts/activate      # Windows (Git Bash)
# source venv/bin/activate        # Linux / macOS

# 2. Závislosti
pip install -r requirements.txt

# 3. Premenné prostredia
cp .env.example .env
# vyplň SECRET_KEY (vygeneruj príkazom v .env.example)

# 4. Inicializácia databázy
python init_db.py
```

## Spustenie

```bash
uvicorn app.main:app --reload
```

Aplikácia beží na http://127.0.0.1:8000/

## Štruktúra

```
app/
├── main.py            # Litestar app + konfigurácia
├── db.py              # async SQLAlchemy engine/session
├── models.py          # modely User, Category, Word
├── schemas.py         # Pydantic schémy
├── session_config.py  # konfigurácia session
└── auth/
    ├── routes.py      # endpointy (auth, kategórie, slovíčka, testy, import)
    ├── security.py    # JWT (kľúč z .env)
    ├── service.py     # hashovanie hesiel (bcrypt)
    └── templates/     # Jinja2 šablóny
init_db.py             # jednorazová inicializácia DB
requirements.txt
```

## Bezpečnosť

`SECRET_KEY` (podpis JWT) a `DATABASE_URL` sa načítavajú z `.env` (mimo gitu).
Databáza (`*.db`), `__pycache__` a virtuálne prostredie sa necommitujú.

> Pozn.: Virtuálne prostredie pomenuj `venv` (nie `.env`), aby sa nepomýlilo
> s konfiguračným súborom `.env`.
