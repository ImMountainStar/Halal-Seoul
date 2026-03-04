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
                stock_qty=20,
                is_active=True,
            ),
            Product(
                product_id="p-002",
                name="Halal Kimchi Dumpling",
                price=10900,
                description="Sample product",
                stock_qty=12,
                is_active=True,
            ),
        ]

    def list_products(self, q: str | None = None, limit: int = 20) -> list[Product]:
        rows = [p for p in self._products if p.is_active]
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
