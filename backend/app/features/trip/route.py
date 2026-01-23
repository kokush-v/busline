from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.roles import RoleChecker, UserRole
from app.features.trip.schemas import (
    TripCreate,
    TripRead,
    TripReadPublic,
    TripUpdate,
)
from app.features.trip.service import TripService

router = APIRouter(prefix='/trips', tags=['Trips'])

# TODO: Apply admin_only dependency to appropriate routes
admin_only = RoleChecker([UserRole.ADMIN])


@router.get('', response_model=list[TripReadPublic])
async def get_many_trips(service: TripService = Depends()):
    """Get all trips (public access)."""
    return await service.get_many_trips()


@router.get('/{trip_id}', response_model=TripReadPublic)
async def get_one_trip(trip_id: UUID, service: TripService = Depends()):
    """Get a specific trip by ID (public access)."""
    return await service.get_one_trip(trip_id)


@router.post(
    '',
    response_model=TripRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_trip(payload: TripCreate, service: TripService = Depends()):
    """Create a new trip (Admin only)."""
    return await service.create_trip(payload)


@router.put(
    '/{trip_id}',
    response_model=TripRead,
)
async def update_trip(trip_id: UUID, payload: TripUpdate, service: TripService = Depends()):
    """Update a trip (Admin only)."""
    return await service.update_trip(trip_id, payload)


@router.delete(
    '/{trip_id}',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_trip(trip_id: UUID, service: TripService = Depends()):
    """Delete a trip (Admin only)."""
    await service.delete_trip(trip_id)
