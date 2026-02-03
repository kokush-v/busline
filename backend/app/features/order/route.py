from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.core.aws.cognito import get_cognito_service
from app.features.order.schemas import OrderRead
from app.features.order.service import OrderService
from app.features.ticket.schemas import TicketRead
from app.features.user.enums import UserRoleGroups

cognito_service = get_cognito_service()
router = APIRouter(prefix='/orders', tags=['Orders'])


@router.get('/{order_id}', response_model=OrderRead)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Get order details by ID."""
    return await service.get_order(order_id)


@router.post('/{order_id}/pay', response_model=OrderRead)
async def pay_order(
    order_id: UUID,
    service: OrderService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Process payment for an order (mock implementation)."""
    return await service.pay_order(order_id)


@router.delete('/{order_id}', status_code=status.HTTP_204_NO_CONTENT)
async def cancel_order(
    order_id: UUID,
    service: OrderService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Cancel an order and release its seats."""
    await service.cancel_order(order_id)


@router.get('/{order_id}/tickets', response_model=list[TicketRead])
async def get_order_tickets(
    order_id: UUID,
    service: OrderService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Get all tickets for a specific order."""
    return await service.get_order_tickets(order_id)
