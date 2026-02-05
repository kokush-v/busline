from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.aws.cognito import get_cognito_service
from app.features.auth.schemas import CognitoUser
from app.features.seat.schemas import ReserveSeatRequest, ReserveSeatResponse, SeatRead
from app.features.seat.service import SeatService
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/seats', tags=['Seats'])


@router.get('/{seat_id}', response_model=SeatRead)
async def get_seat(seat_id: UUID, service: SeatService = Depends()):
    """Get seat details by ID."""
    return await service.get_seat(seat_id)


@router.post('/reserve', response_model=ReserveSeatResponse, status_code=status.HTTP_201_CREATED)
async def reserve_seats(
    payload: ReserveSeatRequest,
    service: SeatService = Depends(),
    user: CognitoUser = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Reserve multiple seats for a trip."""
    return await service.reserve(payload, user_id=UUID(user.sub))
