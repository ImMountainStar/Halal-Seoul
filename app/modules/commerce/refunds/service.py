from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.core.exceptions import BadRequestError, UnauthorizedError
from app.modules.commerce.orders.repository import repo as orders_repo
from app.modules.commerce.refunds.models import Refund, RefundItem
from app.modules.commerce.refunds.repository import repo
from app.modules.commerce.refunds.schemas import RefundItemResponse, RefundResponse


class RefundsService:
    def create_full_refund(self, user_id: str, order_id: str, reason: str) -> RefundResponse:
        order = orders_repo.get_order_by_id(order_id)
        if not order:
            raise BadRequestError("Order not found")
        if order.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this order")
        if order.status != "paid":
            raise BadRequestError("Only paid orders can be refunded")
        existing_refunds = repo.list_refunds_by_order(order_id)
        if existing_refunds:
            raise BadRequestError("Refund already requested for this order")

        refund = Refund(
            refund_id=str(uuid4()),
            order_id=order_id,
            refund_type="full",
            amount=order.amount_total,
            status="requested",
            reason=reason,
            created_at=datetime.now(UTC),
            items=[
                RefundItem(
                    order_item_id=item.order_item_id,
                    quantity=item.quantity,
                    amount=item.line_total,
                )
                for item in order.items
            ],
        )
        repo.create_refund(refund)
        order.status = "cancel_requested"
        orders_repo.save_order(order)
        return self._to_response(refund)

    def create_partial_refund(
        self,
        user_id: str,
        order_id: str,
        items: list[tuple[str, int]],
        reason: str,
    ) -> RefundResponse:
        order = orders_repo.get_order_by_id(order_id)
        if not order:
            raise BadRequestError("Order not found")
        if order.user_id != user_id:
            raise UnauthorizedError("Not allowed to access this order")
        if order.status != "paid":
            raise BadRequestError("Only paid orders can be refunded")
        if not items:
            raise BadRequestError("Refund items are required")
        existing_refunds = repo.list_refunds_by_order(order_id)
        refunded_quantities: dict[str, int] = {}
        for existing_refund in existing_refunds:
            if existing_refund.refund_type == "full":
                raise BadRequestError("Refund already requested for this order")
            for item in existing_refund.items:
                refunded_quantities[item.order_item_id] = refunded_quantities.get(item.order_item_id, 0) + item.quantity

        refund_items: list[RefundItem] = []
        for order_item_id, quantity in items:
            order_item = next((item for item in order.items if item.order_item_id == order_item_id), None)
            if not order_item:
                raise BadRequestError("Order item not found")
            remaining_quantity = order_item.quantity - refunded_quantities.get(order_item_id, 0)
            if quantity > remaining_quantity:
                raise BadRequestError("Refund quantity exceeds order quantity")

            refund_items.append(
                RefundItem(
                    order_item_id=order_item_id,
                    quantity=quantity,
                    amount=order_item.unit_price * quantity,
                )
            )

        refund = Refund(
            refund_id=str(uuid4()),
            order_id=order_id,
            refund_type="partial",
            amount=sum(item.amount for item in refund_items),
            status="requested",
            reason=reason,
            created_at=datetime.now(UTC),
            items=refund_items,
        )
        repo.create_refund(refund)
        return self._to_response(refund)

    def _to_response(self, refund: Refund) -> RefundResponse:
        return RefundResponse(
            refund_id=refund.refund_id,
            order_id=refund.order_id,
            refund_type=refund.refund_type,
            amount=refund.amount,
            status=refund.status,
            reason=refund.reason,
            created_at=refund.created_at,
            items=[
                RefundItemResponse(
                    order_item_id=item.order_item_id,
                    quantity=item.quantity,
                    amount=item.amount,
                )
                for item in refund.items
            ],
        )


service = RefundsService()
