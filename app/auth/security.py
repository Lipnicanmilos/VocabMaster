# app/auth/security.py

"""Bezpečnostné nástroje: JWT generovanie a validácia."""

from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

# Silný tajný kľúč – nahraď vo výrobe!
SECRET_KEY = "supertajneheslo123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Vytvorenie JWT tokenu."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str) -> Optional[dict]:
    """Overenie platnosti tokenu."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
