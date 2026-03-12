from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.modules.commerce.cart.models import Cart, CartItem


class InMemoryCartRepository:
    def __init__(self) -> None:
        self._carts: dict[str, Cart] = {}

    def get_cart(self, user_id: str) -> Cart:
        cart = self._carts.get(user_id)
        if cart is None:
            cart = Cart(cart_id=str(uuid4()), user_id=user_id, updated_at=datetime.now(UTC), items=[])
            self._carts[user_id] = cart
        return cart

    def save_cart(self, cart: Cart) -> Cart:
        cart.updated_at = datetime.now(UTC)
        self._carts[cart.user_id] = cart
        return cart

    def reset_cart(self, user_id: str) -> Cart:
        cart = Cart(cart_id=str(uuid4()), user_id=user_id, updated_at=datetime.now(UTC), items=[])
        self._carts[user_id] = cart
        return cart

    def get_cart_item(self, user_id: str, cart_item_id: str) -> CartItem | None:
        cart = self.get_cart(user_id)
        for item in cart.items:
            if item.cart_item_id == cart_item_id:
                return item
        return None


repo = InMemoryCartRepository()
