from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.aws.cognito import get_cognito_service
from app.features.stop.schemas import (
    StopCreate,
    StopListResponse,
    StopQueryParams,
    StopRead,
    StopSearchParams,
    StopSearchResponse,
    StopUpdate,
)
from app.features.stop.service import StopService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/stops', tags=['Stops'])


@router.get('', response_model=StopListResponse)
async def get_stops(
    params: StopQueryParams = Depends(),
    service: StopService = Depends(),
):
    """Get a list of stops with optional search and pagination (public access)."""
    stops, total = await service.get_stops(params)

    return StopListResponse(
        items=stops,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )


@router.get('/search', response_model=StopSearchResponse)
async def search_stops(
    params: StopSearchParams = Depends(),
    service: StopService = Depends(),
):
    """Public endpoint for searching stops with lazy loading."""
    return await service.search_stops(params)


@router.get('/{stop_id}', response_model=StopRead)
async def get_stop(stop_id: UUID, service: StopService = Depends()):
    return await service.get_stop(stop_id)


@router.post(
    '',
    response_model=StopRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_stop(
    payload: StopCreate,
    service: StopService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.create_stop(payload)


@router.put(
    '/{stop_id}',
    response_model=StopRead,
)
async def update_stop(
    stop_id: UUID,
    payload: StopUpdate,
    service: StopService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    return await service.update_stop(stop_id, payload)


@router.delete(
    '/{stop_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_stop(
    stop_id: UUID,
    service: StopService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.ADMIN])),
):
    await service.delete_stop(stop_id)
