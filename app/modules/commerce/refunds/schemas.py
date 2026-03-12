from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


RefundStatus = Literal["requested", "approved", "rejected", "completed"]


class CreateRefundRequest(BaseModel):
    order_id: str = Field(min_length=1)
    refund_type: Literal["full"]
    reason: str = Field(min_length=1)


class PartialRefundItemRequest(BaseModel):
    order_item_id: str = Field(min_length=1)
    quantity: int = Field(gt=0)


class CreatePartialRefundRequest(BaseModel):
    order_id: str = Field(min_length=1)
    items: list[PartialRefundItemRequest]
    reason: str = Field(min_length=1)


class RefundItemResponse(BaseModel):
    order_item_id: str
    quantity: int
    amount: int


class RefundResponse(BaseModel):
    refund_id: str
    order_id: str
    refund_type: Literal["full", "partial"]
    amount: int
    status: RefundStatus
    reason: str
    created_at: datetime
    items: list[RefundItemResponse]
