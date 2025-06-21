from sanic import Sanic
from sanic.response import json
from sanic_ext import Extend


def create_app() -> Sanic:
    """Создание и настройка приложения Sanic"""
    app = Sanic("paysystem")

    # Расширения
    Extend(app)

    # Простой тестовый роут
    @app.get("/health")
    async def health_check(request):
        return json({"status": "ok", "message": "Server is running"})

    @app.get("/")
    async def root(request):
        return json({"message": "Payment System API", "status": "running"})

    # Добавляем все роуты
    try:
        from app.routes.auth import auth_bp
        from app.routes.users import users_bp
        from app.routes.admin import admin_bp
        from app.routes.webhooks import webhooks_bp

        app.blueprint(auth_bp)
        app.blueprint(users_bp)
        app.blueprint(admin_bp)
        app.blueprint(webhooks_bp)
    except Exception as e:
        print(f"Failed to load routes: {e}")

    # Обработчик ошибок
    @app.exception(Exception)
    async def exception_handler(request, exception):
        print(f"Exception: {exception}")
        return json({"error": "Internal server error"}), 500

    return app


if __name__ == "__main__":
    from app.config import Config

    app = create_app()
    app.run(host=Config.HOST, port=Config.PORT, debug=True, single_process=True)
