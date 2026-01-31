from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.features.ticket.schemas import CreatePdfRequest, PdfStatusResponse, TicketRead, TicketUpdate
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


@router.post('/{ticket_id}/pdf', response_model=PdfStatusResponse)
async def trigger_pdf_generation(
    ticket_id: UUID,
    body: CreatePdfRequest = CreatePdfRequest(),
    service: TicketService = Depends(),
):
    """Trigger PDF generation for a ticket."""
    return await service.trigger_pdf_generation(ticket_id, body)


@router.get('/{ticket_id}/pdf')
async def download_ticket_pdf(ticket_id: UUID, service: TicketService = Depends()):
    """Download ticket PDF file."""
    pdf_stream = await service.stream_ticket_pdf(ticket_id)
    return StreamingResponse(
        pdf_stream,
        media_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="ticket-{ticket_id}.pdf"'},
    )
