from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.modules.commerce.cart.repository import repo as cart_repo
from app.modules.commerce.orders.models import Order, OrderItem, ShippingAddress
from app.modules.commerce.orders.repository import repo
from app.modules.commerce.orders.schemas import (
    CreateOrderResponse,
    OrderDetailResponse,
    OrderItemResponse,
    OrderListItemResponse,
    OrderListResponse,
    ShippingAddressResponse,
)


class OrdersService:
    def create_order(
        self,
        user_id: str,
        cart_id: str,
        recipient: str,
        phone: str,
        line1: str,
        line2: str | None,
        postal_code: str,
        customs_clearance_number: str | None,
    ) -> CreateOrderResponse:
        cart = cart_repo.get_cart(user_id)
        if cart.cart_id != cart_id:
            raise BadRequestError("Cart not found")
        if not cart.items:
            raise BadRequestError("Cart is empty")

        created_at = datetime.now(UTC)
        items = [
            OrderItem(
                order_item_id=str(uuid4()),
                product_id=item.product_id,
                product_name=item.product_name,
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.unit_price * item.quantity,
            )
            for item in cart.items
        ]
        order = Order(
            order_id=str(uuid4()),
            order_number=self._generate_order_number(),
            user_id=user_id,
            cart_id=cart_id,
            status="pending",
            amount_total=sum(item.line_total for item in items),
            currency="KRW",
            customs_clearance_number=customs_clearance_number,
            shipping_address=ShippingAddress(
                recipient=recipient,
                phone=phone,
                line1=line1,
                line2=line2,
                postal_code=postal_code,
            ),
            created_at=created_at,
            updated_at=created_at,
            items=items,
        )
        repo.create_order(order)
        cart_repo.reset_cart(user_id)
        return CreateOrderResponse(order_id=order.order_id, status=order.status, amount_total=order.amount_total)

    def get_order(self, user_id: str, order_id: str) -> OrderDetailResponse:
        order = repo.get_order_by_id(order_id)
        if not order:
            raise BadRequestError("Order not found")
        if order.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this order")
        return self._to_detail(order)

    def list_orders(self, user_id: str, limit: int) -> OrderListResponse:
        if limit < 1 or limit > 100:
            raise BadRequestError("limit must be between 1 and 100")
        items = [
            OrderListItemResponse(
                order_id=order.order_id,
                order_number=order.order_number,
                status=order.status,
                amount_total=order.amount_total,
                currency=order.currency,
                created_at=order.created_at,
            )
            for order in repo.list_orders_by_user(user_id, limit)
        ]
        return OrderListResponse(items=items, next_cursor=None)

    def cancel_order(self, user_id: str, order_id: str, reason: str) -> OrderDetailResponse:
        _ = reason
        order = repo.get_order_by_id(order_id)
        if not order:
            raise BadRequestError("Order not found")
        if order.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this order")
        if order.status == "canceled":
            raise BadRequestError("Order already canceled")
        if order.status == "cancel_requested":
            raise BadRequestError("Order cancellation already requested")

        if order.status == "paid":
            order.status = "cancel_requested"
        elif order.status == "pending":
            order.status = "canceled"
        else:
            raise BadRequestError("Order cannot be canceled")

        repo.save_order(order)
        return self._to_detail(order)

    def mark_paid(self, user_id: str, order_id: str) -> Order:
        order = repo.get_order_by_id(order_id)
        if not order:
            raise BadRequestError("Order not found")
        if order.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this order")
        if order.status != "pending":
            raise BadRequestError("Order is not payable")
        order.status = "paid"
        repo.save_order(order)
        return order

    def _to_detail(self, order: Order) -> OrderDetailResponse:
        return OrderDetailResponse(
            order_id=order.order_id,
            order_number=order.order_number,
            status=order.status,
            amount_total=order.amount_total,
            currency=order.currency,
            customs_clearance_number=order.customs_clearance_number,
            shipping_address=ShippingAddressResponse(
                recipient=order.shipping_address.recipient,
                phone=order.shipping_address.phone,
                line1=order.shipping_address.line1,
                line2=order.shipping_address.line2,
                postal_code=order.shipping_address.postal_code,
            ),
            created_at=order.created_at,
            updated_at=order.updated_at,
            items=[
                OrderItemResponse(
                    order_item_id=item.order_item_id,
                    product_id=item.product_id,
                    product_name=item.product_name,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                    line_total=item.line_total,
                )
                for item in order.items
            ],
        )

    def _generate_order_number(self) -> str:
        return f"HS-{datetime.now(UTC).strftime('%Y%m%d')}-{str(uuid4())[:8]}"


service = OrdersService()
