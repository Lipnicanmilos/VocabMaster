# app/models.py

"""Definuje databázové modely pre aplikáciu."""

# from datetime import datetime
# from sqlalchemy import String, DateTime
# from sqlalchemy.orm import Mapped, mapped_column, declarative_base

# Base = declarative_base()

# class User(Base):
#     """Model používateľa v databáze."""

#     __tablename__ = "users"

#     id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
#     email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
#     hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
#     created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

#     def __repr__(self) -> str:
#         return f"<User(id={self.id}, email={self.email})>"

# app/models.py

"""Definuje databázové modely pre aplikáciu."""

from datetime import datetime
from sqlalchemy import String, DateTime, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base  # ✅ správny import


class User(Base):
    """Model používateľa v databáze."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    categories = relationship("Category", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

class Category(Base):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="categories")
    words = relationship("Word", back_populates="category")


class Word(Base):
    __tablename__ = "words"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sk: Mapped[str] = mapped_column(String, nullable=False)
    en: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[int] = mapped_column(Integer, default=1)  # 1: neviem, 2: opakovať, 3: viem
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("categories.id"))

    category = relationship("Category", back_populates="words")
