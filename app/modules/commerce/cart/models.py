from dataclasses import dataclass
from datetime import datetime


@dataclass
class CartItem:
    cart_item_id: str
    product_id: str
    product_name: str
    unit_price: int
    quantity: int
    added_at: datetime


@dataclass
class Cart:
    cart_id: str
    user_id: str
    updated_at: datetime
    items: list[CartItem]
