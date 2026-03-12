from fastapi import APIRouter, Depends, Query, status

from app.modules.auth.dependencies import get_current_user_id
from app.modules.commerce.orders.schemas import (
    CancelOrderRequest,
    CreateOrderRequest,
    CreateOrderResponse,
    OrderDetailResponse,
    OrderListResponse,
)
from app.modules.commerce.orders.service import service

router = APIRouter()


@router.post("", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CreateOrderRequest,
    user_id: str = Depends(get_current_user_id),
) -> CreateOrderResponse:
    return service.create_order(
        user_id=user_id,
        cart_id=payload.cart_id,
        recipient=payload.shipping_address.recipient,
        phone=payload.shipping_address.phone,
        line1=payload.shipping_address.line1,
        line2=payload.shipping_address.line2,
        postal_code=payload.shipping_address.postal_code,
        customs_clearance_number=payload.customs_clearance_number,
    )


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(order_id: str, user_id: str = Depends(get_current_user_id)) -> OrderDetailResponse:
    return service.get_order(user_id=user_id, order_id=order_id)


@router.get("", response_model=OrderListResponse)
def list_orders(
    cursor: str | None = None,
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_id),
) -> OrderListResponse:
    _ = cursor
    return service.list_orders(user_id=user_id, limit=limit)


@router.post("/{order_id}/cancel", response_model=OrderDetailResponse)
def cancel_order(
    order_id: str,
    payload: CancelOrderRequest,
    user_id: str = Depends(get_current_user_id),
) -> OrderDetailResponse:
    return service.cancel_order(user_id=user_id, order_id=order_id, reason=payload.reason)
