from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.roles import RoleChecker, UserRole
from app.features.bus.schemas import (
    BusCreate,
    BusRead,
    BusUpdate,
    PhotoUploadComplete,
    PresignedUrlRequest,
    PresignedUrlResponse,
    TestUploadRequest,
)
from app.features.bus.service import BusService

router = APIRouter(prefix='/buses', tags=['Buses'])

admin_only = RoleChecker([UserRole.ADMIN])


@router.get('', response_model=list[BusRead])
async def get_many_buses(service: BusService = Depends()):
    return await service.get_many_buses()


@router.get('/{bus_id}', response_model=BusRead)
async def get_one_bus(bus_id: UUID, service: BusService = Depends()):
    return await service.get_one_bus(bus_id)


@router.post(
    '',
    response_model=BusRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_bus(payload: BusCreate, service: BusService = Depends()):
    return await service.create_bus(payload)


@router.put(
    '/{bus_id}',
    response_model=BusRead,
)
async def update_bus(bus_id: UUID, payload: BusUpdate, service: BusService = Depends()):
    return await service.update_bus(bus_id, payload)


@router.delete(
    '/{bus_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bus(bus_id: UUID, service: BusService = Depends()):
    await service.delete_bus(bus_id)


@router.post(
    '/upload-url',
    response_model=PresignedUrlResponse,
)
async def get_image_upload_url(request: PresignedUrlRequest, service: BusService = Depends()):
    return await service.generate_presigned_upload_url(request)


@router.post(
    '/{bus_id}/image/confirm',
    response_model=BusRead,
)
async def confirm_image_upload(bus_id: UUID, payload: PhotoUploadComplete, service: BusService = Depends()):
    return await service.confirm_image_upload(bus_id, payload.photo_key)


@router.delete(
    '/{bus_id}/image',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(bus_id: UUID, service: BusService = Depends()):
    await service.delete_image(bus_id)


# TODO: Remove this test endpoint in production
@router.post('/test-upload', response_model=dict)
async def test_upload_to_s3(
    upload_url: str = Form(...),
    fields: str = Form(...),
    file: UploadFile = File(...),
    service: BusService = Depends(),
):
    import json

    fields_dict = json.loads(fields)
    request = TestUploadRequest(upload_url=upload_url, fields=fields_dict)
    return await service.test_upload_to_s3(request, file)
