from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
import httpx

from app.core.aws.cognito import get_cognito_service
from app.core.exeptions.server import ServerException
from app.features.auth.schemas import CognitoUser
from app.features.order.schemas import OrderListResponse, OrderPaymentResponse, OrderQueryParams, OrderRead
from app.features.order.service import OrderService
from app.features.ticket.schemas import TicketRead
from app.features.user.enums import UserRoleGroups
from app.settings.env import get_env_settings

cognito_service = get_cognito_service()
env_settings = get_env_settings()
router = APIRouter(prefix='/orders', tags=['Orders'])


@router.get('/{order_id}', response_model=OrderRead)
async def get_order(
    order_id: UUID,
    service: OrderService = Depends(),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    """Get order details by ID."""
    return await service.get_order(order_id)


@router.post('/{order_id}/pay', response_model=OrderPaymentResponse)
async def pay_order(
    order_id: UUID,
    status_override: str | None = Query(
        None,
        description='Override payment status (PAID, FAILED, PROCESSING). If None, randomly selected.',
    ),
    _: dict = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                env_settings.PAYMENT_WEBHOOK_URL,
                json={
                    'order_id': str(order_id),
                    'status': status_override or 'PAID',
                    'payment_method': 'mock',
                },
            )
    except Exception as err:
        raise ServerException(
            message='Failed to process payment',
            status=502,
            details={'error': str(err)},
        ) from err

    return OrderPaymentResponse(
        order_id=order_id,
        message=f'Payment request submitted. Status: {status_override or "PAID"}',
    )


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


@router.get('/', response_model=OrderListResponse)
async def get_user_orders(
    service: OrderService = Depends(),
    params: OrderQueryParams = Depends(),
    user: CognitoUser = Depends(cognito_service.roles_required([UserRoleGroups.USER])),
):
    orders, total = await service.get_user_orders(user_id=user.sub, params=params)
    return OrderListResponse(
        items=orders,
        total=total,
        limit=params.limit,
        offset=params.offset,
    )
