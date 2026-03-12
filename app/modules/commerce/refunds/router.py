from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user_id
from app.modules.commerce.refunds.schemas import (
    CreatePartialRefundRequest,
    CreateRefundRequest,
    RefundResponse,
)
from app.modules.commerce.refunds.service import service

router = APIRouter()


@router.post("", response_model=RefundResponse)
def create_refund(
    payload: CreateRefundRequest,
    user_id: str = Depends(get_current_user_id),
) -> RefundResponse:
    return service.create_full_refund(user_id=user_id, order_id=payload.order_id, reason=payload.reason)


@router.post("/partial", response_model=RefundResponse)
def create_partial_refund(
    payload: CreatePartialRefundRequest,
    user_id: str = Depends(get_current_user_id),
) -> RefundResponse:
    return service.create_partial_refund(
        user_id=user_id,
        order_id=payload.order_id,
        items=[(item.order_item_id, item.quantity) for item in payload.items],
        reason=payload.reason,
    )
