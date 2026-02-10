from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.core.aws.cognito import get_cognito_service
from app.features.ticket.schemas import CreatePdfRequest, PdfStatusResponse
from app.features.ticket.service import TicketService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/tickets', tags=['Tickets'])


@router.post('/{ticket_id}/pdf', response_model=PdfStatusResponse)
async def trigger_pdf_generation(
    ticket_id: UUID,
    body: CreatePdfRequest = CreatePdfRequest(),
    service: TicketService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Trigger PDF generation for a ticket."""
    return await service.trigger_pdf_generation(ticket_id, body)


@router.get('/{ticket_id}/pdf')
async def download_ticket_pdf(
    ticket_id: UUID,
    service: TicketService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Download ticket PDF file."""
    pdf_stream = await service.stream_ticket_pdf(ticket_id)
    return StreamingResponse(
        pdf_stream,
        media_type='application/pdf',
        headers={'Content-Disposition': f'inline; filename="ticket-{ticket_id}.pdf"'},
    )
