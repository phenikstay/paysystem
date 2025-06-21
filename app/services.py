import hashlib
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.auth import AuthService
from app.config import Config
from app.models import User, Account, Payment
from app.schemas import UserCreate, UserUpdate


class UserService:
    """Сервис для работы с пользователями"""

    @staticmethod
    async def create_user(session: AsyncSession, user_data: UserCreate) -> User:
        """Создание пользователя"""
        # Проверяем существование пользователя
        stmt = select(User).where(User.email == user_data.email)
        existing_user = await session.execute(stmt)
        if existing_user.scalar_one_or_none():
            raise ValueError("User with this email already exists")

        # Создаем пользователя
        hashed_password = AuthService.hash_password(user_data.password)
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            password_hash=hashed_password,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_users(session: AsyncSession) -> List[User]:
        """Получение всех пользователей"""
        stmt = select(User).options(selectinload(User.accounts))
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def update_user(
        session: AsyncSession, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Обновление пользователя"""
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            return None

        if user_data.email:
            user.email = user_data.email
        if user_data.full_name:
            user.full_name = user_data.full_name
        if user_data.password:
            user.password_hash = AuthService.hash_password(user_data.password)

        await session.commit()
        await session.refresh(user)
        return user

    @staticmethod
    async def delete_user(session: AsyncSession, user_id: int) -> bool:
        """Удаление пользователя"""
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            return False

        await session.delete(user)
        await session.commit()
        return True


class AccountService:
    """Сервис для работы со счетами"""

    @staticmethod
    async def get_user_accounts(session: AsyncSession, user_id: int) -> List[Account]:
        """Получение счетов пользователя"""
        stmt = select(Account).where(Account.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_or_create_account(
        session: AsyncSession, user_id: int, account_id: int
    ) -> Account:
        """Получение или создание счета"""
        stmt = select(Account).where(
            Account.id == account_id, Account.user_id == user_id
        )
        result = await session.execute(stmt)
        account = result.scalar_one_or_none()

        if not account:
            account = Account(id=account_id, user_id=user_id, balance=Decimal("0.00"))
            session.add(account)
            await session.commit()
            await session.refresh(account)

        return account


class PaymentService:
    """Сервис для работы с платежами"""

    @staticmethod
    async def get_user_payments(session: AsyncSession, user_id: int) -> List[Payment]:
        """Получение платежей пользователя"""
        stmt = select(Payment).where(Payment.user_id == user_id)
        result = await session.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def process_payment(
        session: AsyncSession,
        transaction_id: str,
        user_id: int,
        account_id: int,
        amount: Decimal,
    ) -> Payment:
        """Обработка платежа"""
        # Проверяем уникальность транзакции
        stmt = select(Payment).where(Payment.transaction_id == transaction_id)
        result = await session.execute(stmt)
        existing_payment = result.scalar_one_or_none()

        if existing_payment:
            raise ValueError("Transaction already processed")

        # Получаем или создаем счет
        account = await AccountService.get_or_create_account(
            session, user_id, account_id
        )

        # Создаем платеж
        payment = Payment(
            transaction_id=transaction_id,
            account_id=account_id,
            user_id=user_id,
            amount=amount,
        )
        session.add(payment)

        # Обновляем баланс счета
        account.balance += amount

        await session.commit()
        await session.refresh(payment)
        return payment


class WebhookService:
    """Сервис для работы с вебхуками"""

    @staticmethod
    def verify_signature(
        transaction_id: str,
        user_id: int,
        account_id: int,
        amount: Decimal,
        signature: str,
    ) -> bool:
        """Проверка подписи вебхука"""
        # Формируем строку для хеширования в алфавитном порядке ключей
        # Приводим amount к string форме для консистентности
        amount_str = (
            str(amount) if isinstance(amount, Decimal) else str(Decimal(str(amount)))
        )
        data_string = f"{account_id}{amount_str}{transaction_id}{user_id}{Config.WEBHOOK_SECRET_KEY}"

        # Вычисляем SHA256 хеш
        calculated_signature = hashlib.sha256(data_string.encode()).hexdigest()

        return calculated_signature == signature
