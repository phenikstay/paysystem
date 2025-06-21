import asyncio
import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from app.models import *  # Импортируем все модели

# Объект конфигурации Alembic, который предоставляет
# доступ к значениям в используемом .ini файле
config = context.config

# Устанавливаем URL базы данных из переменной окружения
database_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://paysystem_user:password@localhost:5432/paysystem",
)
config.set_main_option("sqlalchemy.url", database_url)

# Интерпретация конфигурационного файла для логирования Python
# Эта строка настраивает логгеры
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Добавляем объект MetaData наших моделей здесь
# для поддержки 'autogenerate'
target_metadata = Base.metadata

# Другие значения из конфигурации, определенные потребностями env.py,
# могут быть получены:
# my_important_option = config.get_main_option("my_important_option")
# ... и т.д.


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме.

    Это настраивает контекст только с URL
    и без Engine, хотя Engine также приемлем
    здесь. Пропуская создание Engine
    нам даже не нужен DBAPI.

    Вызовы context.execute() здесь выводят данную строку в
    вывод скрипта.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Выполнение миграций с подключением"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """В этом сценарии нам нужно создать Engine
    и связать подключение с контекстом.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
