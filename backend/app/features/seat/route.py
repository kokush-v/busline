from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.features.seat.schemas import ReserveSeatRequest, ReserveSeatResponse, SeatRead
from app.features.seat.service import SeatService

router = APIRouter(prefix='/seats', tags=['Seats'])


@router.get('/{seat_id}', response_model=SeatRead)
async def get_seat(seat_id: UUID, service: SeatService = Depends()):
    """Get seat details by ID."""
    return await service.get_seat(seat_id)


@router.post('/reserve', response_model=ReserveSeatResponse, status_code=status.HTTP_201_CREATED)
async def reserve_seats(payload: ReserveSeatRequest, service: SeatService = Depends()):
    """Reserve multiple seats for a trip."""
    return await service.reserve(payload)
