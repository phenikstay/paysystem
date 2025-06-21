from functools import wraps

from sanic import Request, response

from app.auth import AuthService


def require_auth(roles=None):
    """Декоратор для проверки аутентификации"""
    if roles is None:
        roles = []

    def decorator(f):
        @wraps(f)
        async def decorated_function(request: Request, *args, **kwargs):
            # Получаем токен из заголовка
            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return response.json(
                    {"error": "Missing or invalid authorization header"}, status=401
                )

            token = auth_header.split(" ")[1]

            # Декодируем токен
            payload = AuthService.decode_token(token)
            if not payload:
                return response.json({"error": "Invalid or expired token"}, status=401)

            # Проверяем роль если указана
            user_role = payload.get("role")
            if roles and user_role not in roles:
                return response.json({"error": "Insufficient permissions"}, status=403)

            # Проверяем существование пользователя
            from app.database import async_session

            async with async_session() as session:
                current_user = await AuthService.get_current_user(
                    session, payload.get("user_id"), user_role
                )
                if not current_user:
                    return response.json({"error": "User not found"}, status=401)

                # Добавляем информацию о пользователе в request
                request.ctx.current_user = current_user
                request.ctx.user_role = user_role

                return await f(request, *args, **kwargs)

        return decorated_function

    return decorator


def require_user_auth(f):
    """Декоратор только для пользователей"""
    return require_auth(["user"])(f)


def require_admin_auth(f):
    """Декоратор только для администраторов"""
    return require_auth(["admin"])(f)
