from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from app.core.roles import RoleChecker, UserRole
from app.features.stop.schemas import StopCreate, StopRead, StopUpdate
from app.features.stop.service import StopService

router = APIRouter(prefix='/stops', tags=['Stops'])

# TODO: Apply admin_only dependency to appropriate routes
admin_only = RoleChecker([UserRole.ADMIN])


@router.get('', response_model=list[StopRead])
async def get_stops(
    search: Annotated[str | None, Query(description='Search stops by city or stop name')] = None,
    service: StopService = Depends(),
):
    """Get a list of stops with optional search by city or stop name (public access)."""
    return await service.get_stops(search=search)


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
