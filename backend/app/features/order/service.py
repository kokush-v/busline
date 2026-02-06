from asyncio import TaskGroup
from datetime import UTC, datetime
import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import and_, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.order.schemas import OrderCreate
from app.features.seat.enums import SeatStatus
from app.features.seat.models import Seat
from app.features.ticket.models import Ticket
from app.features.ticket.service import TicketService
from app.utils.decorators import transactional

logger = logging.getLogger(__name__)


class OrderService:
    """Service for managing orders and reservations."""

    def __init__(self, session: AsyncSession = Depends(get_db_session), ticket_service: TicketService = Depends()):
        self._session = session
        self._ticket_service = ticket_service

    async def get_order(self, order_id: UUID) -> Order:
        result = await self._session.execute(select(Order).where(Order.id == order_id))
        return result.scalars().one()

    async def get_user_orders(self, user_id: UUID) -> list[Order]:
        result = await self._session.execute(select(Order).where(Order.user_id == user_id))
        orders = result.scalars().all()
        return orders

    async def _create_order(self, payload: OrderCreate, user_id: UUID) -> Order:
        order_stmt = insert(Order).values(**payload.model_dump(), user_id=user_id).returning(Order)
        order_result = await self._session.execute(order_stmt)
        order = order_result.scalar_one()
        return order

    async def __trigger_pdf_for_ticket(self, ticket, order_id: UUID) -> None:
        try:
            from app.features.ticket.schemas import CreatePdfRequest

            await self._ticket_service.trigger_pdf_generation(ticket_id=ticket.id, body=CreatePdfRequest(force=False))
        except Exception as e:
            logger.error(
                f'Failed to trigger PDF generation for ticket {ticket.id}: {str(e)}',
                exc_info=True,
                extra={'ticket_id': str(ticket.id), 'order_id': str(order_id)},
            )

    async def __trigger_pdf_for_all_tickets(self, order_id: UUID) -> None:
        tickets = await self.get_order_tickets(order_id)
        async with TaskGroup() as tg:
            for ticket in tickets:
                tg.create_task(self.__trigger_pdf_for_ticket(ticket, order_id))

    @transactional
    async def pay_order(self, order_id: UUID) -> Order:
        order_stmt = select(Order).where(Order.id == order_id).with_for_update()
        result = await self._session.execute(order_stmt)
        order = result.scalar_one()

        if order.expires_at and datetime.now(UTC) > order.expires_at:
            await self._cancel_order(order.id)
            raise ServerException(message='Order has expired', status=400)

        if order.status == OrderStatus.PAID:
            return order

        order.status = OrderStatus.PAID
        order.payment_method = 'mock'
        order.updated_at = datetime.now(UTC)

        seat_ids_subquery = select(Ticket.seat_id).where(Ticket.order_id == order_id)
        update_seats_stmt = update(Seat).where(Seat.id.in_(seat_ids_subquery)).values(status=SeatStatus.SOLD)

        await self._session.execute(update_seats_stmt)

        await self.__trigger_pdf_for_all_tickets(order.id)

        return order

    @transactional
    async def cancel_order(self, order_id: UUID) -> None:
        """Cancel an order and release its seats."""
        order = await self._session.execute(select(Order).where(Order.id == order_id).with_for_update())
        order.scalars().one()

        await self._cancel_order(order_id)

    @transactional
    async def _cancel_order(self, order_id: UUID) -> None:
        """Internal method to cancel an order."""
        stmt = update(Order).where(Order.id == order_id).values(status=OrderStatus.CANCELLED)
        await self._session.execute(stmt)

        seat_ids_subquery = select(Ticket.seat_id).where(Ticket.order_id == order_id)
        update_seats_stmt = update(Seat).where(Seat.id.in_(seat_ids_subquery)).values(status=SeatStatus.FREE)
        await self._session.execute(update_seats_stmt)

    async def __cancel_all_expired_orders(self, order_ids: list[UUID]) -> None:
        async with TaskGroup() as tg:
            for order_id in order_ids:
                tg.create_task(self._cancel_order(order_id))

    @transactional
    async def cleanup_expired_orders(self) -> int:
        """
        Clean up expired orders.

        Returns the number of orders cancelled.
        """
        now = datetime.now(UTC)

        result = await self._session.execute(
            select(Order.id)
            .where(
                and_(
                    Order.status == OrderStatus.PENDING,
                    Order.expires_at < now,
                )
            )
            .with_for_update()
        )
        expired_order_ids = result.scalars().all()

        await self.__cancel_all_expired_orders(expired_order_ids)

        return len(expired_order_ids)

    async def get_order_tickets(self, order_id: UUID) -> list[Ticket]:
        stmt = select(Ticket).join(Order, Ticket.order_id == Order.id).where(Order.id == order_id)
        result = await self._session.execute(stmt)

        return result.scalars().all()
