from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db_session
from app.features.ticket.models import Ticket
from app.features.ticket.schemas import TicketCreate, TicketUpdate
from app.utils.decorators import transactional


class TicketService:
    """Service for managing tickets."""

    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self._session = session

    async def _create_many_tickets(self, tickets_data: list[TicketCreate]) -> list[Ticket]:
        tickets_dicts = [t.model_dump() for t in tickets_data]
        ticket_stmt = insert(Ticket).values(tickets_dicts).returning(Ticket)
        tickets_result = await self._session.execute(ticket_stmt)
        tickets = tickets_result.scalars().all()
        return tickets

    async def get_ticket(self, ticket_id: UUID) -> Ticket:
        """Get ticket details by ID."""
        result = await self._session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalars().one()

    @transactional
    async def update_ticket(self, ticket_id: UUID, payload: TicketUpdate) -> Ticket:
        """Update ticket details using Core-style DML."""

        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_ticket(ticket_id)

        stmt = update(Ticket).where(Ticket.id == ticket_id).values(**update_data).returning(Ticket)

        result = await self._session.execute(stmt)
        ticket = result.scalar_one()

        await self._session.commit()
        return ticket
