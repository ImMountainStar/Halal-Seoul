from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user_id
from app.modules.commerce.payments.schemas import (
    PaymentConfirmRequest,
    PaymentConfirmResponse,
)

router = APIRouter()


@router.post("/confirm", response_model=PaymentConfirmResponse)
def confirm_payment(
    payload: PaymentConfirmRequest,
    user_id: str = Depends(get_current_user_id),
) -> PaymentConfirmResponse:
    _ = user_id
    return PaymentConfirmResponse(
        status="confirmed",
        order_id=payload.order_id,
        payment_key=payload.payment_key,
        amount=payload.amount,
        provider=payload.provider,
    )
