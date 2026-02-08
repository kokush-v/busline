from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, UploadFile, status

from app.core.aws.cognito import get_cognito_service
from app.features.bus.schemas import (
    BusCreate,
    BusListResponse,
    BusQueryParams,
    BusRead,
    BusUpdate,
    PhotoUploadComplete,
    PresignedUrlRequest,
    PresignedUrlResponse,
    TestUploadRequest,
)
from app.features.bus.service import BusService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/buses', tags=['Buses'])


@router.get('', response_model=BusListResponse)
async def get_buses(
    params: BusQueryParams = Depends(),
    service: BusService = Depends(),
):
    """Get buses with filtering, sorting, and pagination."""
    buses, total = await service.get_buses(params)

    return BusListResponse(
        items=buses,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get('/{bus_id}', response_model=BusRead)
async def get_bus(bus_id: UUID, service: BusService = Depends()):
    return await service.get_bus(bus_id)


@router.post(
    '',
    response_model=BusRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_bus(
    payload: BusCreate,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.create_bus(payload)


@router.put(
    '/{bus_id}',
    response_model=BusRead,
)
async def update_bus(
    bus_id: UUID,
    payload: BusUpdate,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.update_bus(bus_id, payload)


@router.delete(
    '/{bus_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_bus(
    bus_id: UUID,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    await service.delete_bus(bus_id)


@router.post(
    '/{bus_id}/upload-url',
    response_model=PresignedUrlResponse,
)
async def get_image_upload_url(
    bus_id: UUID,
    request: PresignedUrlRequest,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.generate_presigned_upload_url(bus_id, request)


@router.post(
    '/{bus_id}/image/save',
    response_model=BusRead,
)
async def image_save(
    bus_id: UUID,
    payload: PhotoUploadComplete,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.image_save(bus_id, payload.photo_key)


@router.delete(
    '/{bus_id}/image',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_image(
    bus_id: UUID,
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    await service.delete_image(bus_id)


# TODO: Remove this test endpoint in production
@router.post('/test-upload', response_model=dict)
async def test_upload_to_s3(
    upload_url: str = Form(...),
    fields: str = Form(...),
    file: UploadFile = File(...),
    service: BusService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    import json

    fields_dict = json.loads(fields)
    request = TestUploadRequest(upload_url=upload_url, fields=fields_dict)
    return await service.test_upload_to_s3(request, file)
