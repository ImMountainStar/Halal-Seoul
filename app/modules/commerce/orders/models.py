from dataclasses import dataclass
from datetime import datetime


@dataclass
class ShippingAddress:
    recipient: str
    phone: str
    line1: str
    line2: str | None
    postal_code: str


@dataclass
class OrderItem:
    order_item_id: str
    product_id: str
    product_name: str
    unit_price: int
    quantity: int
    line_total: int


@dataclass
class Order:
    order_id: str
    order_number: str
    user_id: str
    cart_id: str
    status: str
    amount_total: int
    currency: str
    customs_clearance_number: str | None
    shipping_address: ShippingAddress
    created_at: datetime
    updated_at: datetime
    items: list[OrderItem]
