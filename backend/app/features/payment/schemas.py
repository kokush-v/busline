from uuid import UUID

from pydantic import BaseModel

from app.features.order.enums import OrderStatus


class PaymentWebhookRequest(BaseModel):
    """Schema for simulated payment webhook payload."""

    order_id: UUID
    status: OrderStatus
    external_payment_id: str | None = None
    payment_method: str | None = None
