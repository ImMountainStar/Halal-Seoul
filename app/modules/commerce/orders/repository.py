from __future__ import annotations

from datetime import UTC, datetime

from app.modules.commerce.orders.models import Order


class InMemoryOrdersRepository:
    def __init__(self) -> None:
        self._orders: list[Order] = []

    def create_order(self, order: Order) -> Order:
        self._orders.insert(0, order)
        return order

    def get_order_by_id(self, order_id: str) -> Order | None:
        for order in self._orders:
            if order.order_id == order_id:
                return order
        return None

    def list_orders_by_user(self, user_id: str, limit: int) -> list[Order]:
        rows = [order for order in self._orders if order.user_id == user_id]
        return rows[:limit]

    def save_order(self, order: Order) -> Order:
        order.updated_at = datetime.now(UTC)
        return order


repo = InMemoryOrdersRepository()
