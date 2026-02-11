from asyncio import TaskGroup
import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete, desc, func, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.order.enums import OrderStatus
from app.features.order.models import Order
from app.features.order.schemas import OrderCreate, OrderQueryParams
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

    async def get_user_orders(self, user_id: UUID, params: OrderQueryParams) -> tuple[list[Order], int]:
        query = select(Order).where(Order.user_id == user_id)
        query = self.__apply_status_filter(query, params)

        total = await self.__get_total_count(query)

        query = query.order_by(desc(Order.created_at))
        query = self.__apply_pagination(query, params)

        result = await self._session.execute(query)
        orders = list(result.scalars().all())
        return orders, total

    def __apply_status_filter(self, query, params: OrderQueryParams):
        if params.statuses:
            query = query.where(Order.status.in_(params.statuses))
        return query

    async def __get_total_count(self, query) -> int:
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self._session.execute(count_query)
        return total_result.scalar_one()

    def __apply_pagination(self, query, params: OrderQueryParams):
        return query.limit(params.limit).offset(params.offset)

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

    async def _trigger_pdf_for_order_tickets(self, order_id: UUID) -> None:
        tickets = await self.get_order_tickets(order_id)
        async with TaskGroup() as tg:
            for ticket in tickets:
                tg.create_task(self.__trigger_pdf_for_ticket(ticket, order_id))

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

        await self._delete_order_tickets(order_id)

    async def _delete_order_tickets(self, order_id: UUID) -> None:
        delete_stmt = delete(Ticket).where(Ticket.order_id == order_id)
        await self._session.execute(delete_stmt)

    async def get_order_tickets(self, order_id: UUID) -> list[Ticket]:
        stmt = select(Ticket).join(Order, Ticket.order_id == Order.id).where(Order.id == order_id)
        result = await self._session.execute(stmt)

        return result.scalars().all()
