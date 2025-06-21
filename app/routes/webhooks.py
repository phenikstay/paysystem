from sanic import Blueprint, Request, response
from sanic_ext import validate

from app.database import async_session
from app.schemas import WebhookRequest, PaymentResponse
from app.services import PaymentService, WebhookService
from app.utils import custom_json_serializer

webhooks_bp = Blueprint("webhooks", url_prefix="/api/webhooks")


@webhooks_bp.post("/payment")
@validate(json=WebhookRequest)
async def process_payment_webhook(request: Request, body: WebhookRequest):
    """Обработка вебхука платежа"""
    # Проверяем подпись
    if not WebhookService.verify_signature(
        body.transaction_id,
        body.user_id,
        body.account_id,
        body.amount,
        body.signature,
    ):
        return response.json({"error": "Invalid signature"}, status=400)

    async with async_session() as session:
        try:
            payment = await PaymentService.process_payment(
                session,
                body.transaction_id,
                body.user_id,
                body.account_id,
                body.amount,
            )

            return response.json(
                {
                    "status": "success",
                    "message": "Payment processed successfully",
                    "payment": PaymentResponse.model_validate(payment).model_dump(),
                },
                default=custom_json_serializer,
            )

        except ValueError as e:
            if "already processed" in str(e):
                return response.json(
                    {"error": "Transaction already processed"}, status=409
                )
            return response.json({"error": str(e)}, status=400)
        except Exception as e:
            return response.json({"error": "Internal server error"}, status=500)
