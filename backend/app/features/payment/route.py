from fastapi import APIRouter, Depends

from app.features.order.schemas import OrderRead
from app.features.payment.schemas import PaymentWebhookRequest
from app.features.payment.service import PaymentService

router = APIRouter(prefix='/payments', tags=['Payments'])


@router.post('/webhook', response_model=OrderRead)
async def payment_webhook(payload: PaymentWebhookRequest, service: PaymentService = Depends()):
    """Simulated payment webhook endpoint (no auth)."""
    return await service.process_payment_webhook(payload)
