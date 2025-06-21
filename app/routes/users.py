from sanic import Blueprint, Request, response

from app.database import async_session
from app.middleware import require_user_auth
from app.schemas import UserResponse, AccountResponse, PaymentResponse
from app.services import AccountService, PaymentService
from app.utils import custom_json_serializer

users_bp = Blueprint("users", url_prefix="/api/users")


@users_bp.get("/me")
@require_user_auth
async def get_current_user(request: Request):
    """Получение данных о текущем пользователе"""
    user = request.ctx.current_user
    user_data = UserResponse.model_validate(user).model_dump()
    return response.json(user_data, default=custom_json_serializer)


@users_bp.get("/me/accounts")
@require_user_auth
async def get_user_accounts(request: Request):
    """Получение счетов пользователя"""
    user = request.ctx.current_user
    async with async_session() as session:
        accounts = await AccountService.get_user_accounts(session, user.id)
        accounts_data = [
            AccountResponse.model_validate(account).model_dump() for account in accounts
        ]
        return response.json(accounts_data, default=custom_json_serializer)


@users_bp.get("/me/payments")
@require_user_auth
async def get_user_payments(request: Request):
    """Получение платежей пользователя"""
    user = request.ctx.current_user
    async with async_session() as session:
        payments = await PaymentService.get_user_payments(session, user.id)
        payments_data = [
            PaymentResponse.model_validate(payment).model_dump() for payment in payments
        ]
        return response.json(payments_data, default=custom_json_serializer)
