from uuid import UUID

from fastapi import Depends, HTTPException, UploadFile, status
import httpx
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.s3_service import S3Service, get_s3_service
from app.database.db import get_db_session
from app.features.bus.models import Bus
from app.features.bus.schemas import (
    BusCreate,
    BusUpdate,
    PresignedUrlRequest,
    PresignedUrlResponse,
    TestUploadRequest,
)
from app.settings.env import get_env_settings


class BusService:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
        s3_service: S3Service = Depends(get_s3_service),
    ):
        self._session = session
        self._settings = get_env_settings()
        self._s3_service = s3_service

    async def get_many_buses(self) -> list[Bus]:
        result = await self._session.execute(select(Bus))
        return list(result.scalars().all())

    async def get_one_bus(self, bus_id: UUID) -> Bus:
        result = await self._session.execute(select(Bus).where(Bus.id == bus_id))
        bus = result.scalars().one_or_none()
        if bus is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Bus not found')
        return bus

    async def create_bus(self, payload: BusCreate) -> Bus:
        result = await self._session.execute(select(Bus).filter(Bus.number_plate == payload.number_plate))
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Bus with this number plate already exists',
            )

        stmt = insert(Bus).values(**payload.model_dump()).returning(Bus)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def update_bus(self, bus_id: UUID, payload: BusUpdate) -> Bus:
        await self.get_one_bus(bus_id)

        update_data = payload.model_dump(exclude_unset=True)
        if 'number_plate' in update_data:
            result = await self._session.execute(
                select(Bus).filter(Bus.number_plate == update_data['number_plate'], Bus.id != bus_id)
            )
            conflict = result.scalar_one_or_none()
            if conflict:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail='Bus with this number plate already exists',
                )

        stmt = update(Bus).where(Bus.id == bus_id).values(**update_data).returning(Bus)
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def delete_bus(self, bus_id: UUID) -> None:
        bus = await self.get_one_bus(bus_id)

        if bus.photo_url:
            photo_key = self._s3_service.extract_key_from_url(bus.photo_url, self._settings.S3_PHOTOS_BUCKET)
            if photo_key:
                await self._s3_service.delete_object(self._settings.S3_PHOTOS_BUCKET, photo_key)

        if bus.thumbnail_url:
            thumbnail_key = self._s3_service.extract_key_from_url(
                bus.thumbnail_url, self._settings.S3_THUMBNAILS_BUCKET
            )
            if thumbnail_key:
                await self._s3_service.delete_object(self._settings.S3_THUMBNAILS_BUCKET, thumbnail_key)

        stmt = delete(Bus).where(Bus.id == bus_id)
        await self._session.execute(stmt)
        await self._session.commit()

    async def generate_presigned_upload_url(self, request: PresignedUrlRequest) -> PresignedUrlResponse:
        """Generate a presigned URL for uploading a photo to S3."""
        allowed_content_types = ['image/jpeg', 'image/png']
        if request.content_type not in allowed_content_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f'Invalid content type. Allowed types: {", ".join(allowed_content_types)}',
            )

        try:
            presigned_post = await self._s3_service.generate_presigned_upload_url(
                bucket=self._settings.S3_PHOTOS_BUCKET,
                key=request.filename,
                content_type=request.content_type,
                max_size=10485760,  # 10MB
            )

            return PresignedUrlResponse(
                upload_url=presigned_post['url'],
                photo_key=request.filename,
                fields=presigned_post['fields'],
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to generate presigned URL: {e}',
            ) from e

    async def update_media_urls(self, bus_id: UUID, photo_key: str) -> Bus:
        bus = await self.get_one_bus(bus_id)

        await self._delete_old_media(bus)

        photo_url = (
            f'https://{self._settings.S3_PHOTOS_BUCKET}.s3.{self._settings.AWS_REGION}.amazonaws.com/{photo_key}'
        )
        thumbnail_url = (
            f'https://{self._settings.S3_THUMBNAILS_BUCKET}.s3.{self._settings.AWS_REGION}.amazonaws.com/{photo_key}'
        )

        stmt = (
            update(Bus).where(Bus.id == bus_id).values(photo_url=photo_url, thumbnail_url=thumbnail_url).returning(Bus)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalars().one()

    async def confirm_image_upload(self, bus_id: UUID, photo_key: str) -> Bus:
        """Confirm image upload/update and update bus record with photo URL."""
        return await self.update_media_urls(bus_id, photo_key)

    async def delete_image(self, bus_id: UUID) -> None:
        """Delete the image for a bus."""
        bus = await self.get_one_bus(bus_id)

        if bus.photo_url:
            photo_key = self._s3_service.extract_key_from_url(bus.photo_url, self._settings.S3_PHOTOS_BUCKET)
            if photo_key:
                await self._s3_service.delete_object(self._settings.S3_PHOTOS_BUCKET, photo_key)

        stmt = update(Bus).where(Bus.id == bus_id).values(photo_url=None).returning(Bus)
        await self._session.execute(stmt)
        await self._session.commit()

    async def _delete_old_media(self, bus: Bus) -> None:
        """Helper to delete old photo and thumbnail from S3."""
        if bus.photo_url:
            photo_key = self._s3_service.extract_key_from_url(bus.photo_url, self._settings.S3_PHOTOS_BUCKET)
            if photo_key:
                await self._s3_service.delete_object(self._settings.S3_PHOTOS_BUCKET, photo_key)

        if bus.thumbnail_url:
            thumbnail_key = self._s3_service.extract_key_from_url(
                bus.thumbnail_url, self._settings.S3_THUMBNAILS_BUCKET
            )
            if thumbnail_key:
                await self._s3_service.delete_object(self._settings.S3_THUMBNAILS_BUCKET, thumbnail_key)

    async def test_upload_to_s3(self, request: TestUploadRequest, file: UploadFile) -> dict:
        """Test endpoint to upload a file to S3 using presigned URL."""
        try:
            file_content = await file.read()

            async with httpx.AsyncClient() as client:
                # Prepare form data
                files = {'file': (file.filename, file_content, file.content_type)}
                data = request.fields

                # Upload to S3
                response = await client.post(request.upload_url, data=data, files=files)

                if response.status_code == 204:
                    return {
                        'success': True,
                        'message': 'File uploaded successfully to S3',
                        'status_code': response.status_code,
                    }
                else:
                    return {
                        'success': False,
                        'message': 'Upload failed',
                        'status_code': response.status_code,
                        'response': response.text,
                    }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f'Failed to upload file: {str(e)}',
            ) from e
