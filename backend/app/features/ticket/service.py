import logging
from uuid import UUID

from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.aws.lambda_service import LambdaService, get_lambda_service
from app.core.aws.s3_service import S3Service, get_s3_service
from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.ticket.enums import PdfStatus
from app.features.ticket.models import Ticket
from app.features.ticket.schemas import CreatePdfRequest, PdfStatusResponse, TicketCreate, TicketUpdate
from app.settings.env import get_env_settings
from app.utils.decorators import transactional

logger = logging.getLogger(__name__)


class TicketService:
    """Service for managing tickets."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        s3_service: S3Service = Depends(get_s3_service),
        lambda_service: LambdaService = Depends(get_lambda_service),
    ):
        self._session = session
        self._s3_service = s3_service
        self._lambda_service = lambda_service
        self._settings = get_env_settings()

    async def _create_many_tickets(self, tickets_data: list[TicketCreate]) -> list[Ticket]:
        tickets_dicts = [t.model_dump() for t in tickets_data]
        ticket_stmt = insert(Ticket).values(tickets_dicts).returning(Ticket)
        tickets_result = await self._session.execute(ticket_stmt)
        tickets = tickets_result.scalars().all()
        return tickets

    async def get_ticket(self, ticket_id: UUID) -> Ticket:
        result = await self._session.execute(select(Ticket).where(Ticket.id == ticket_id))
        return result.scalars().one()

    @transactional
    async def update_ticket(self, ticket_id: UUID, payload: TicketUpdate) -> Ticket:
        update_data = payload.model_dump(exclude_unset=True)

        if not update_data:
            return await self.get_ticket(ticket_id)

        stmt = update(Ticket).where(Ticket.id == ticket_id).values(**update_data).returning(Ticket)

        result = await self._session.execute(stmt)
        ticket = result.scalar_one()

        await self._session.commit()
        return ticket

    async def trigger_pdf_generation(self, ticket_id: UUID, body: CreatePdfRequest) -> PdfStatusResponse:
        """
        Trigger PDF generation via AWS Lambda.

        Lambda handles ALL status transitions:
        - Lambda sets GENERATING when it starts (lambda_function.py:359)
        - Lambda sets READY on success (lambda_function.py:378)
        - Lambda sets FAILED on error (lambda_function.py:417)
        - Lambda Destination (TicketPdfFailureHandler) sets FAILED on timeout/crash

        FastAPI just invokes Lambda fire-and-forget and returns current status.
        Client should poll GET /tickets/{id} to check status updates.
        """
        ticket = await self.get_ticket(ticket_id)

        if ticket.pdf_status == PdfStatus.READY and ticket.pdf_s3_key and not body.force:
            logger.info(f'PDF already ready for ticket {ticket_id}')
            return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.READY)

        if ticket.pdf_status == PdfStatus.GENERATING and not body.force:
            logger.info(f'PDF generation already in progress for ticket {ticket_id}')
            return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.GENERATING)

        try:
            await self._lambda_service.trigger_ticket_generator_lambda(ticket_id=ticket_id, force=body.force)
            logger.info(f'Lambda invoked successfully for ticket {ticket_id}')
        except Exception as e:
            logger.error(f'Failed to invoke Lambda for ticket {ticket_id}: {e}', exc_info=True)
            raise ServerException(
                message='Failed to invoke PDF generation Lambda',
                status=500,
                details={'error': str(e), 'ticket_id': str(ticket_id)},
            ) from e

        return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.GENERATING)

    async def stream_ticket_pdf(self, ticket_id: UUID):
        ticket = await self.get_ticket(ticket_id)

        if ticket.pdf_status != PdfStatus.READY or not ticket.pdf_s3_key:
            raise ServerException(
                message='PDF is not available yet',
                status=404,
                details={'ticket_id': str(ticket_id), 'pdf_status': ticket.pdf_status},
            )

        await self._s3_service.validate_object_access(
            bucket=self._settings.S3_TICKETS_BUCKET,
            key=ticket.pdf_s3_key,
        )

        return self._s3_service.download_file(
            bucket=self._settings.S3_TICKETS_BUCKET,
            key=ticket.pdf_s3_key,
        )
