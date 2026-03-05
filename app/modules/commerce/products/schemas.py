from pydantic import BaseModel


class ProductItem(BaseModel):
    product_id: str
    name: str
    price: int
    sale_status: str


class ProductListResponse(BaseModel):
    items: list[ProductItem]
    next_cursor: str | None = None


class ProductDetailResponse(ProductItem):
    description: str | None = None
