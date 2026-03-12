from fastapi import APIRouter, Depends

from app.modules.auth.dependencies import get_current_user_id
from app.modules.commerce.cart.schemas import (
    AddCartItemRequest,
    CartResponse,
    UpdateCartItemRequest,
)
from app.modules.commerce.cart.service import service

router = APIRouter()


@router.get("", response_model=CartResponse)
def get_cart(user_id: str = Depends(get_current_user_id)) -> CartResponse:
    return service.get_cart(user_id)


@router.post("/items", response_model=CartResponse)
def add_cart_item(
    payload: AddCartItemRequest,
    user_id: str = Depends(get_current_user_id),
) -> CartResponse:
    return service.add_item(user_id=user_id, product_id=payload.product_id, quantity=payload.quantity)


@router.patch("/items/{cart_item_id}", response_model=CartResponse)
def update_cart_item(
    cart_item_id: str,
    payload: UpdateCartItemRequest,
    user_id: str = Depends(get_current_user_id),
) -> CartResponse:
    return service.update_item(user_id=user_id, cart_item_id=cart_item_id, quantity=payload.quantity)


@router.delete("/items/{cart_item_id}", response_model=CartResponse)
def delete_cart_item(
    cart_item_id: str,
    user_id: str = Depends(get_current_user_id),
) -> CartResponse:
    return service.delete_item(user_id=user_id, cart_item_id=cart_item_id)
