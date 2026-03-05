from dataclasses import dataclass


@dataclass
class Product:
    product_id: str
    name: str
    price: int
    description: str | None
    sale_status: str
