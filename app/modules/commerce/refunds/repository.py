from __future__ import annotations

from app.modules.commerce.refunds.models import Refund


class InMemoryRefundsRepository:
    def __init__(self) -> None:
        self._refunds: list[Refund] = []

    def create_refund(self, refund: Refund) -> Refund:
        self._refunds.insert(0, refund)
        return refund

    def list_refunds_by_order(self, order_id: str) -> list[Refund]:
        return [refund for refund in self._refunds if refund.order_id == order_id]


repo = InMemoryRefundsRepository()
