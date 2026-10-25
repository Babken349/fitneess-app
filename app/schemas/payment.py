from decimal import Decimal

from pydantic import BaseModel, Field


class PaymentCreate(BaseModel):
    amount: Decimal = Field(
        gt=0,
        decimal_places=2,
    )


class PaymentResponse(BaseModel):
    id: int
    payment_id: str
    amount: Decimal
    currency: str
    status: str
    description: str | None

    model_config = {
        "from_attributes": True,
    }


class PaymentCreateResponse(BaseModel):
    payment_id: str
    amount: Decimal
    currency: str
    status: str
    confirmation_url: str