from datetime import UTC, datetime

from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.order.service import OrderService
from app.features.payment.schemas import PaymentWebhookRequest
from app.features.seat.enums import SeatStatus
from app.features.seat.models import Seat
from app.features.ticket.models import Ticket
from app.utils.decorators import transactional


class PaymentService:
    """Service for simulated payment processing and webhooks."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        order_service: OrderService = Depends(),
    ):
        self._session = session
        self._order_service = order_service

    def _build_update_values(self, status: OrderStatus, webhook_updates: dict) -> dict:
        """Build update values dict with status and optional webhook fields."""
        values = {
            'status': status,
            'updated_at': datetime.now(UTC),
        }
        values.update(
            {key: value for key, value in webhook_updates.items() if key in {'external_payment_id', 'payment_method'}}
        )
        return values

    async def _update_seats_status(self, order_id, seat_status: SeatStatus) -> None:
        """Update all seats for order to given status."""
        seat_ids_subquery = select(Ticket.seat_id).where(Ticket.order_id == order_id)
        update_seats_stmt = update(Seat).where(Seat.id.in_(seat_ids_subquery)).values(status=seat_status)
        await self._session.execute(update_seats_stmt)

    async def _handle_paid_payment(self, order_id, webhook_updates: dict) -> Order:
        """Handle payment confirmation (PAID status)."""
        update_values = self._build_update_values(OrderStatus.PAID, webhook_updates)
        update_order_stmt = update(Order).where(Order.id == order_id).values(**update_values).returning(Order)
        updated_order = (await self._session.execute(update_order_stmt)).scalar_one()

        await self._update_seats_status(order_id, SeatStatus.SOLD)

        await self._order_service._trigger_pdf_for_order_tickets(order_id)
        return updated_order

    async def _handle_failed_payment(self, order_id, webhook_updates: dict) -> Order:
        """Handle payment failure (FAILED status)."""
        update_values = self._build_update_values(OrderStatus.FAILED, webhook_updates)
        update_order_stmt = update(Order).where(Order.id == order_id).values(**update_values).returning(Order)
        updated_order = (await self._session.execute(update_order_stmt)).scalar_one()

        await self._update_seats_status(order_id, SeatStatus.FREE)
        return updated_order

    async def _handle_cancelled_payment(self, order_id, webhook_updates: dict) -> Order:
        """Handle payment cancellation (CANCELLED status)."""
        update_values = self._build_update_values(OrderStatus.CANCELLED, webhook_updates)
        update_order_stmt = update(Order).where(Order.id == order_id).values(**update_values).returning(Order)
        updated_order = (await self._session.execute(update_order_stmt)).scalar_one()

        await self._update_seats_status(order_id, SeatStatus.FREE)
        return updated_order

    async def _handle_default_payment(self, order_id, status: OrderStatus, webhook_updates: dict) -> Order:
        """Handle other payment statuses (PROCESSING, PENDING, etc)."""
        update_values = self._build_update_values(status, webhook_updates)
        update_order_stmt = update(Order).where(Order.id == order_id).values(**update_values).returning(Order)
        return (await self._session.execute(update_order_stmt)).scalar_one()

    @transactional
    async def process_payment_webhook(self, payload: PaymentWebhookRequest) -> Order:
        """Process a simulated payment webhook payload."""
        order_stmt = select(Order).where(Order.id == payload.order_id).with_for_update()
        result = await self._session.execute(order_stmt)
        order = result.scalar_one()

        if order.expires_at and datetime.now(UTC) > order.expires_at:
            await self._order_service.cancel_order(order.id)
            raise ServerException(message='Order has expired', status=400)

        webhook_updates = payload.model_dump(exclude_none=True)

        if payload.status == OrderStatus.PAID:
            return await self._handle_paid_payment(order.id, webhook_updates)

        if payload.status == OrderStatus.FAILED:
            return await self._handle_failed_payment(order.id, webhook_updates)

        if payload.status == OrderStatus.CANCELLED:
            return await self._handle_cancelled_payment(order.id, webhook_updates)

        return await self._handle_default_payment(order.id, payload.status, webhook_updates)
