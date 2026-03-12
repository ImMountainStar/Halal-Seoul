from datetime import datetime

from pydantic import BaseModel, Field


class CartItemResponse(BaseModel):
    cart_item_id: str
    product_id: str
    product_name: str
    unit_price: int
    quantity: int
    line_total: int
    added_at: datetime


class CartResponse(BaseModel):
    cart_id: str
    items: list[CartItemResponse]
    item_count: int
    amount_total: int
    updated_at: datetime | None = None


class AddCartItemRequest(BaseModel):
    product_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class UpdateCartItemRequest(BaseModel):
    quantity: int = Field(gt=0)
