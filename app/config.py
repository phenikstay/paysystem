import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Класс конфигурации приложения с переменными окружения"""

    # База данных
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://paysystem_user:password@localhost:5432/paysystem",
    )

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRATION_DELTA = 3600  # 1 час

    # Webhook secret key
    WEBHOOK_SECRET_KEY = os.getenv("WEBHOOK_SECRET_KEY", "gfdmhghif38yrf9ew0jkf32")

    # Sanic
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
