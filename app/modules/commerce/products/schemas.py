from pydantic import BaseModel, Field


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


class AdminProductCreateRequest(BaseModel):
    name: str = Field(min_length=1)
    price: int = Field(ge=0)
    description: str | None = None
    sale_status: str


class AdminProductUpdateRequest(BaseModel):
    name: str | None = None
    price: int | None = Field(default=None, ge=0)
    description: str | None = None
    sale_status: str | None = None
