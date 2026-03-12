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

    def create_product(self, name: str, price: int, description: str | None, sale_status: str):
        self._validate_sale_status(sale_status)
        return repo.create_product(name=name, price=price, description=description, sale_status=sale_status)

    def update_product(
        self,
        product_id: str,
        name: str | None,
        price: int | None,
        description: str | None,
        sale_status: str | None,
    ):
        if sale_status is not None:
            self._validate_sale_status(sale_status)
        product = repo.update_product(
            product_id=product_id,
            name=name,
            price=price,
            description=description,
            sale_status=sale_status,
        )
        if not product:
            raise BadRequestError("Product not found")
        return product

    def _validate_sale_status(self, sale_status: str) -> None:
        if sale_status not in {"노출", "중지", "품절"}:
            raise BadRequestError("Invalid sale_status")


service = ProductsService()
