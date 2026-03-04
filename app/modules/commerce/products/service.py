from app.core.exceptions import BadRequestError
from app.modules.commerce.products.repository import repo


class ProductsService:
    def list_products(self, q: str | None, limit: int) -> list:
        if limit < 1 or limit > 100:
            raise BadRequestError("limit must be between 1 and 100")
        return repo.list_products(q=q, limit=limit)

    def get_product(self, product_id: str):
        product = repo.get_product(product_id)
        if not product:
            raise BadRequestError("Product not found")
        return product


service = ProductsService()
