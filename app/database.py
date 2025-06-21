from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from app.config import Config

# Создание асинхронного движка базы данных
engine = create_async_engine(Config.DATABASE_URL, echo=True, future=True)

# Создание фабрики асинхронных сессий
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy"""

    pass


async def get_session():
    """Генератор для получения асинхронной сессии базы данных"""
    async with async_session() as session:
        yield session
