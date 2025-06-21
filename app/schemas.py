from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


# Настройка для сериализации datetime
class CustomBaseModel(BaseModel):
    """Базовая модель с настройкой сериализации"""

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None,
        },
    )


# Схемы для аутентификации
class LoginRequest(BaseModel):
    """Схема запроса авторизации"""

    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """Схема ответа с JWT токеном"""

    access_token: str
    token_type: str = "bearer"


# Схемы для пользователя
class UserCreate(BaseModel):
    """Схема создания пользователя"""

    email: EmailStr
    full_name: str
    password: str


class UserUpdate(BaseModel):
    """Схема обновления пользователя"""

    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None


class UserResponse(CustomBaseModel):
    """Схема ответа с данными пользователя"""

    id: int
    email: str
    full_name: str
    created_at: datetime


# Схемы для администратора
class AdminResponse(CustomBaseModel):
    """Схема ответа с данными администратора"""

    id: int
    email: str
    full_name: str
    created_at: datetime


# Схемы для счета
class AccountResponse(CustomBaseModel):
    """Схема ответа с данными счета"""

    id: int
    user_id: int
    balance: Decimal
    created_at: datetime


# Схемы для платежа
class PaymentResponse(CustomBaseModel):
    """Схема ответа с данными платежа"""

    id: int
    transaction_id: str
    account_id: int
    user_id: int
    amount: Decimal
    created_at: datetime


# Схема для вебхука
class WebhookRequest(BaseModel):
    """Схема запроса вебхука от платежной системы"""

    transaction_id: str
    user_id: int
    account_id: int
    amount: Decimal = Field(gt=0)
    signature: str


# Расширенные ответы
class UserWithAccountsResponse(UserResponse):
    """Схема пользователя со счетами"""

    accounts: List[AccountResponse] = []


class UserWithPaymentsResponse(UserResponse):
    """Схема пользователя с платежами"""

    payments: List[PaymentResponse] = []
