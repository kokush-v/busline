from uuid import UUID

from fastapi import APIRouter, Depends

from app.features.ticket.schemas import TicketRead, TicketUpdate
from app.features.ticket.service import TicketService

router = APIRouter(prefix='/tickets', tags=['Tickets'])


@router.get('/{ticket_id}', response_model=TicketRead)
async def get_ticket(ticket_id: UUID, service: TicketService = Depends()):
    """Get ticket details by ID."""
    return await service.get_ticket(ticket_id)


@router.patch('/{ticket_id}', response_model=TicketRead)
async def update_ticket(ticket_id: UUID, payload: TicketUpdate, service: TicketService = Depends()):
    """Update ticket details (e.g., passenger info, PDF URL)."""
    return await service.update_ticket(ticket_id, payload)
