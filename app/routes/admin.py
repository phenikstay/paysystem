from sanic import Blueprint, Request, response
from sanic_ext import validate

from app.database import async_session
from app.middleware import require_admin_auth
from app.schemas import (
    AdminResponse,
    UserResponse,
    UserCreate,
    UserUpdate,
    AccountResponse,
)
from app.services import UserService, AccountService
from app.utils import custom_json_serializer

admin_bp = Blueprint("admin", url_prefix="/api/admin")


@admin_bp.get("/me")
@require_admin_auth
async def get_current_admin(request: Request):
    """Получение данных о текущем администраторе"""
    admin = request.ctx.current_user
    admin_data = AdminResponse.model_validate(admin).model_dump()
    return response.json(admin_data, default=custom_json_serializer)


@admin_bp.get("/users")
@require_admin_auth
async def get_users(request: Request):
    """Получение списка всех пользователей"""
    async with async_session() as session:
        users = await UserService.get_users(session)

        users_with_accounts = []
        for user in users:
            user_data = UserResponse.model_validate(user).model_dump()
            accounts = await AccountService.get_user_accounts(session, user.id)
            user_data["accounts"] = [
                AccountResponse.model_validate(account).model_dump()
                for account in accounts
            ]
            users_with_accounts.append(user_data)

        return response.json(users_with_accounts, default=custom_json_serializer)


@admin_bp.post("/users")
@require_admin_auth
@validate(json=UserCreate)
async def create_user(request: Request, body: UserCreate):
    """Создание нового пользователя"""
    async with async_session() as session:
        try:
            user = await UserService.create_user(session, body)
            user_data = UserResponse.model_validate(user).model_dump()
            return response.json(user_data, status=201, default=custom_json_serializer)
        except ValueError as e:
            return response.json({"error": str(e)}, status=400)


@admin_bp.get("/users/<user_id:int>")
@require_admin_auth
async def get_user(request: Request, user_id: int):
    """Получение пользователя по ID"""
    async with async_session() as session:
        user = await UserService.get_user_by_id(session, user_id)
        if not user:
            return response.json({"error": "User not found"}, status=404)
        return response.json(
            UserResponse.model_validate(user).model_dump(),
            default=custom_json_serializer,
        )


@admin_bp.put("/users/<user_id:int>")
@require_admin_auth
@validate(json=UserUpdate)
async def update_user(request: Request, user_id: int, body: UserUpdate):
    """Обновление пользователя"""
    async with async_session() as session:
        try:
            user = await UserService.update_user(session, user_id, body)
            if not user:
                return response.json({"error": "User not found"}, status=404)

            user_data = UserResponse.model_validate(user).model_dump()
            return response.json(user_data, default=custom_json_serializer)
        except ValueError as e:
            return response.json({"error": str(e)}, status=400)


@admin_bp.delete("/users/<user_id:int>")
@require_admin_auth
async def delete_user(request: Request, user_id: int):
    """Удаление пользователя"""
    async with async_session() as session:
        success = await UserService.delete_user(session, user_id)
        if not success:
            return response.json({"error": "User not found"}, status=404)

        return response.json({"message": "User deleted successfully"})
