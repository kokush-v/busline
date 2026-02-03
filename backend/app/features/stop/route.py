from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.roles import RoleChecker, UserRole
from app.features.stop.schemas import StopCreate, StopListResponse, StopQueryParams, StopRead, StopUpdate
from app.features.stop.service import StopService

router = APIRouter(prefix='/stops', tags=['Stops'])

# TODO: Apply admin_only dependency to appropriate routes
admin_only = RoleChecker([UserRole.ADMIN])


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


@router.get('/{stop_id}', response_model=StopRead)
async def get_stop(stop_id: UUID, service: StopService = Depends()):
    return await service.get_stop(stop_id)


@router.post(
    '',
    response_model=StopRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_stop(payload: StopCreate, service: StopService = Depends()):
    return await service.create_stop(payload)


@router.put(
    '/{stop_id}',
    response_model=StopRead,
)
async def update_stop(stop_id: UUID, payload: StopUpdate, service: StopService = Depends()):
    return await service.update_stop(stop_id, payload)


@router.delete(
    '/{stop_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_stop(stop_id: UUID, service: StopService = Depends()):
    await service.delete_stop(stop_id)
