from fastapi import APIRouter, Depends, Header

from app.core.exceptions import BadRequestError
from app.modules.commerce.orders.repository import repo as orders_repo
from app.modules.auth.dependencies import get_current_user_id
from app.modules.commerce.orders.service import service as orders_service
from app.modules.commerce.payments.repository import repo as payments_repo
from app.modules.commerce.payments.schemas import (
    PaymentConfirmRequest,
    PaymentConfirmResponse,
)

router = APIRouter()


@router.post("/confirm", response_model=PaymentConfirmResponse)
def confirm_payment(
    payload: PaymentConfirmRequest,
    idempotency_key: str = Header(alias="Idempotency-Key"),
    user_id: str = Depends(get_current_user_id),
) -> PaymentConfirmResponse:
    signature = payments_repo.build_payload_signature(
        {
            "order_id": payload.order_id,
            "payment_key": payload.payment_key,
            "amount": payload.amount,
            "provider": payload.provider,
        }
    )
    stored = payments_repo.get_by_idempotency_key(idempotency_key)
    if stored:
        stored_signature, stored_response = stored
        if stored_signature != signature:
            raise BadRequestError("Idempotency key reused with different payload")
        return stored_response

    order = orders_repo.get_order_by_id(payload.order_id)
    if not order:
        raise BadRequestError("Order not found")
    if order.user_id != user_id:
        raise BadRequestError("Order not found")
    if payload.amount != order.amount_total:
        raise BadRequestError("Payment amount does not match order total")
    if payments_repo.has_payment_key(payload.payment_key):
        raise BadRequestError("Payment key already used")

    orders_service.mark_paid(user_id=user_id, order_id=payload.order_id)
    payments_repo.save_payment_key(payload.payment_key)
    response = PaymentConfirmResponse(
        status="confirmed",
        order_id=payload.order_id,
        payment_key=payload.payment_key,
        amount=payload.amount,
        provider=payload.provider,
    )
    payments_repo.save_by_idempotency_key(idempotency_key, signature, response)
    return response
