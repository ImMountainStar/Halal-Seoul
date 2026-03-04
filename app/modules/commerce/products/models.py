from dataclasses import dataclass


@dataclass
class Product:
    product_id: str
    name: str
    price: int
    description: str | None
    stock_qty: int
    is_active: bool
