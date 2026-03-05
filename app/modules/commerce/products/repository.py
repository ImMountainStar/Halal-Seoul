from __future__ import annotations

from app.modules.commerce.products.models import Product


class InMemoryProductsRepository:
    def __init__(self) -> None:
        self._products: list[Product] = [
            Product(
                product_id="p-001",
                name="Chicken Sausage",
                price=8900,
                description="Sample product",
                sale_status="노출",
            ),
            Product(
                product_id="p-002",
                name="Halal Kimchi Dumpling",
                price=10900,
                description="Sample product",
                sale_status="품절",
            ),
        ]

    def list_products(self, q: str | None = None, limit: int = 20) -> list[Product]:
        rows = [p for p in self._products if p.sale_status != "중지"]
        if q:
            query = q.lower().strip()
            rows = [p for p in rows if query in p.name.lower()]
        return rows[:limit]

    def get_product(self, product_id: str) -> Product | None:
        for product in self._products:
            if product.product_id == product_id:
                return product
        return None


repo = InMemoryProductsRepository()
