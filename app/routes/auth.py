from sanic import Blueprint, Request, response
from sanic_ext import validate

from app.auth import AuthService
from app.database import async_session
from app.schemas import LoginRequest, TokenResponse

auth_bp = Blueprint("auth", url_prefix="/api/auth")


@auth_bp.post("/user/login")
@validate(json=LoginRequest)
async def user_login(request: Request, body: LoginRequest):
    """Авторизация пользователя"""
    async with async_session() as session:
        user = await AuthService.authenticate_user(session, body.email, body.password)
        if not user:
            return response.json({"error": "Invalid credentials"}, status=401)

        token = AuthService.create_token(user.id, "user")
        return response.json(TokenResponse(access_token=token).model_dump())


@auth_bp.post("/admin/login")
@validate(json=LoginRequest)
async def admin_login(request: Request, body: LoginRequest):
    """Авторизация администратора"""
    async with async_session() as session:
        admin = await AuthService.authenticate_admin(session, body.email, body.password)
        if not admin:
            return response.json({"error": "Invalid credentials"}, status=401)

        token = AuthService.create_token(admin.id, "admin")
        return response.json(TokenResponse(access_token=token).model_dump())
