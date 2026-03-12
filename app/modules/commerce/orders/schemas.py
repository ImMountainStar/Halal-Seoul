from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


OrderStatus = Literal["pending", "paid", "cancel_requested", "canceled"]


class ShippingAddressRequest(BaseModel):
    recipient: str = Field(min_length=1)
    phone: str = Field(min_length=1)
    line1: str = Field(min_length=1)
    line2: str | None = None
    postal_code: str = Field(min_length=1)


class ShippingAddressResponse(ShippingAddressRequest):
    pass


class CreateOrderRequest(BaseModel):
    cart_id: str = Field(min_length=1)
    shipping_address: ShippingAddressRequest
    customs_clearance_number: str | None = None


class OrderItemResponse(BaseModel):
    order_item_id: str
    product_id: str
    product_name: str
    unit_price: int
    quantity: int
    line_total: int


class CreateOrderResponse(BaseModel):
    order_id: str
    status: OrderStatus
    amount_total: int


class OrderDetailResponse(BaseModel):
    order_id: str
    order_number: str
    status: OrderStatus
    amount_total: int
    currency: str
    customs_clearance_number: str | None = None
    shipping_address: ShippingAddressResponse
    created_at: datetime
    updated_at: datetime
    items: list[OrderItemResponse]


class OrderListItemResponse(BaseModel):
    order_id: str
    order_number: str
    status: OrderStatus
    amount_total: int
    currency: str
    created_at: datetime


class OrderListResponse(BaseModel):
    items: list[OrderListItemResponse]
    next_cursor: str | None = None


class CancelOrderRequest(BaseModel):
    reason: str = Field(min_length=1)
