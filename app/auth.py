from datetime import datetime, timedelta
from typing import Optional, Union

import bcrypt
import jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import Config
from app.models import User, Admin


class AuthService:
    """Сервис для аутентификации и авторизации пользователей"""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хеширование пароля"""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))

    @staticmethod
    def create_token(user_id: int, role: str) -> str:
        """Создание JWT токена"""
        payload = {
            "user_id": user_id,
            "role": role,
            "exp": datetime.utcnow() + timedelta(seconds=Config.JWT_EXPIRATION_DELTA),
        }
        return jwt.encode(payload, Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Декодирование JWT токена"""
        try:
            payload = jwt.decode(
                token, Config.JWT_SECRET, algorithms=[Config.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    @staticmethod
    async def authenticate_user(
        session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Аутентификация пользователя"""
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user and AuthService.verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    async def authenticate_admin(
        session: AsyncSession, email: str, password: str
    ) -> Optional[Admin]:
        """Аутентификация администратора"""
        stmt = select(Admin).where(Admin.email == email)
        result = await session.execute(stmt)
        admin = result.scalar_one_or_none()

        if admin and AuthService.verify_password(password, admin.password_hash):
            return admin
        return None

    @staticmethod
    async def get_current_user(
        session: AsyncSession, user_id: int, role: str
    ) -> Optional[Union[User, Admin]]:
        """Получение текущего пользователя по токену"""
        if role == "user":
            stmt = select(User).where(User.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        elif role == "admin":
            stmt = select(Admin).where(Admin.id == user_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        return None
