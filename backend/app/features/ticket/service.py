import json
from uuid import UUID

import aioboto3
from botocore.config import Config
from fastapi import Depends
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exeptions import ServerException
from app.core.s3_service import S3Service, get_s3_service
from app.database.db import get_db_session
from app.features.ticket.enums import PdfStatus
from app.features.ticket.models import Ticket
from app.features.ticket.schemas import CreatePdfRequest, PdfStatusResponse, TicketCreate, TicketUpdate
from app.settings.env import get_env_settings
from app.utils.decorators import transactional


class TicketService:
    """Service for managing tickets."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        s3_service: S3Service = Depends(get_s3_service),
    ):
        self._session = session
        self._s3_service = s3_service
        self._settings = get_env_settings()

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

    @transactional
    async def trigger_pdf_generation(self, ticket_id: UUID, body: CreatePdfRequest) -> PdfStatusResponse:
        """Trigger PDF generation via AWS Lambda."""
        ticket = await self.get_ticket(ticket_id)

        # Idempotent: already ready and not forced
        if ticket.pdf_status == PdfStatus.READY and ticket.pdf_s3_key and not body.force:
            return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.READY)

        # Guard: already in progress
        if ticket.pdf_status == PdfStatus.GENERATING and not body.force:
            return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.GENERATING)

        # Invoke Lambda asynchronously (fire-and-forget)
        payload = json.dumps({'ticket_id': str(ticket_id), 'force': body.force})

        try:
            boto_session = aioboto3.Session()
            async with boto_session.client(
                'lambda',
                aws_access_key_id=self._settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=self._settings.AWS_SECRET_ACCESS_KEY,
                region_name=self._settings.AWS_REGION,
                config=Config(signature_version='v4'),
            ) as lambda_client:
                await lambda_client.invoke(
                    FunctionName=self._settings.TICKET_PDF_LAMBDA_NAME,
                    InvocationType='Event',  # async
                    Payload=payload.encode('utf-8'),
                )
        except Exception as e:
            # Revert status on invoke failure
            revert_stmt = (
                update(Ticket).where(Ticket.id == ticket_id).values(pdf_status=PdfStatus.FAILED, pdf_error=str(e)[:500])
            )
            await self._session.execute(revert_stmt)
            raise ServerException(
                message='Failed to invoke PDF generation',
                status=500,
                details={'error': str(e)},
            ) from e

        return PdfStatusResponse(ticket_id=ticket_id, status=PdfStatus.GENERATING)

    async def stream_ticket_pdf(self, ticket_id: UUID):
        """Stream ticket PDF from S3."""
        ticket = await self.get_ticket(ticket_id)

        if ticket.pdf_status != PdfStatus.READY or not ticket.pdf_s3_key:
            raise ServerException(
                message='PDF is not available yet',
                status=404,
                details={'ticket_id': str(ticket_id), 'pdf_status': ticket.pdf_status},
            )

        return self._s3_service.download_file(
            bucket=self._settings.S3_TICKETS_BUCKET,
            key=ticket.pdf_s3_key,
        )
