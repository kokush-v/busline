from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.common.schemas import EntityModel
from app.features.order.enums import OrderStatus


class OrderBase(BaseModel):
    total_price: Decimal = Field(..., decimal_places=2, ge=0)


class OrderCreate(BaseModel):
    """Schema for creating an order (used in reserve endpoint)."""

    total_price: Decimal = Field(..., decimal_places=2, ge=0)
    expires_at: datetime
    status: OrderStatus = OrderStatus.PENDING


class OrderRead(EntityModel):
    user_id: UUID | None = None
    status: OrderStatus
    total_price: Decimal
    expires_at: datetime | None = None
    external_payment_id: str | None = None
    payment_method: str | None = None


class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    external_payment_id: str | None = None
    payment_method: str | None = None


class OrderPaymentResponse(BaseModel):
    order_id: UUID
    message: str
