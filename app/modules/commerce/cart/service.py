from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.core.exceptions import BadRequestError
from app.modules.commerce.cart.models import Cart, CartItem
from app.modules.commerce.cart.repository import repo
from app.modules.commerce.cart.schemas import CartItemResponse, CartResponse
from app.modules.commerce.products.repository import repo as products_repo


class CartService:
    def get_cart(self, user_id: str) -> CartResponse:
        return self._to_response(repo.get_cart(user_id))

    def add_item(self, user_id: str, product_id: str, quantity: int) -> CartResponse:
        product = products_repo.get_product(product_id)
        if not product or product.sale_status == "중지":
            raise BadRequestError("Product not found")
        if product.sale_status == "품절":
            raise BadRequestError("Product is sold out")

        cart = repo.get_cart(user_id)
        for item in cart.items:
            if item.product_id == product_id:
                item.quantity += quantity
                repo.save_cart(cart)
                return self._to_response(cart)

        cart.items.append(
            CartItem(
                cart_item_id=str(uuid4()),
                product_id=product.product_id,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity,
                added_at=datetime.now(UTC),
            )
        )
        repo.save_cart(cart)
        return self._to_response(cart)

    def update_item(self, user_id: str, cart_item_id: str, quantity: int) -> CartResponse:
        cart = repo.get_cart(user_id)
        item = repo.get_cart_item(user_id, cart_item_id)
        if not item:
            raise BadRequestError("Cart item not found")

        item.quantity = quantity
        repo.save_cart(cart)
        return self._to_response(cart)

    def delete_item(self, user_id: str, cart_item_id: str) -> CartResponse:
        cart = repo.get_cart(user_id)
        before = len(cart.items)
        cart.items = [item for item in cart.items if item.cart_item_id != cart_item_id]
        if len(cart.items) == before:
            raise BadRequestError("Cart item not found")

        repo.save_cart(cart)
        return self._to_response(cart)

    def _to_response(self, cart: Cart) -> CartResponse:
        items = [
            CartItemResponse(
                cart_item_id=item.cart_item_id,
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.unit_price * item.quantity,
                added_at=item.added_at,
            )
            for item in cart.items
        ]
        return CartResponse(
            cart_id=cart.cart_id,
            items=items,
            item_count=sum(item.quantity for item in cart.items),
            amount_total=sum(item.unit_price * item.quantity for item in cart.items),
            updated_at=cart.updated_at,
        )


service = CartService()
