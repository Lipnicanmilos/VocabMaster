"""Pydantic schémy pre aplikáciu."""

from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class UserCreate(BaseModel):
    """Schéma pre registráciu používateľa."""
    email: EmailStr
    password: str = Field(min_length=8)

class UserLogin(BaseModel):
    """Schéma pre prihlásenie používateľa."""
    email: EmailStr
    password: str

class UserRead(BaseModel):
    """Schéma na výstup údajov o používateľovi."""
    id: int
    email: EmailStr

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    """Odpoveď s JWT tokenom."""
    access_token: str
    token_type: str = "bearer"

class ExcelImportResponse(BaseModel):
    """Odpoveď pre import slovíčok z Excel súboru."""
    success: bool
    message: str
    imported_count: int
    skipped_count: int
    errors: List[str] = []
