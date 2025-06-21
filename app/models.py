from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    ForeignKey,
    DateTime,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class User(Base):
    """Модель пользователя системы"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    accounts = relationship(
        "Account", back_populates="user", cascade="all, delete-orphan"
    )


class Admin(Base):
    """Модель администратора системы"""

    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Account(Base):
    """Модель банковского счета пользователя"""

    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    balance = Column(Numeric(precision=10, scale=2), default=0.0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    user = relationship("User", back_populates="accounts")
    payments = relationship("Payment", back_populates="account")


class Payment(Base):
    """Модель платежа (транзакции пополнения счета)"""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(precision=10, scale=2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Отношения
    account = relationship("Account", back_populates="payments")
    user = relationship("User")

    # Уникальность транзакции
    __table_args__ = (UniqueConstraint("transaction_id", name="unique_transaction"),)
