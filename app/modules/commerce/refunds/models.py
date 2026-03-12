from dataclasses import dataclass
from datetime import datetime


@dataclass
class RefundItem:
    order_item_id: str
    quantity: int
    amount: int


@dataclass
class Refund:
    refund_id: str
    order_id: str
    refund_type: str
    amount: int
    status: str
    reason: str
    created_at: datetime
    items: list[RefundItem]
