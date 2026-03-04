from pydantic import BaseModel, Field


class PaymentConfirmRequest(BaseModel):
    order_id: str = Field(min_length=1)
    payment_key: str = Field(min_length=1)
    amount: int = Field(gt=0)
    provider: str = Field(min_length=1)


class PaymentConfirmResponse(BaseModel):
    status: str
    order_id: str
    payment_key: str
    amount: int
    provider: str
