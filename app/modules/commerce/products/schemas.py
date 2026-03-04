from pydantic import BaseModel


class ProductItem(BaseModel):
    product_id: str
    name: str
    price: int


class ProductListResponse(BaseModel):
    items: list[ProductItem]
    next_cursor: str | None = None


class ProductDetailResponse(ProductItem):
    description: str | None = None
    stock_qty: int = 0
    is_active: bool = True
