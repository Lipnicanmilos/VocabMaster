# app/auth/service.py

"""Servisné funkcie pre registráciu a prihlásenie."""

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Zahashuje heslo pomocou bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Overí, či heslo sedí s hashom."""
    return pwd_context.verify(plain_password, hashed_password)
