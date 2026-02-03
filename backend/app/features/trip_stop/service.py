from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exeptions import ServerException
from app.database.db import get_db_session
from app.features.trip_stop.models import TripStop


class TripStopService:
    """Service for managing trip stops."""

    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ):
        self._session = session

    async def validate_stops_exist_in_trip(
        self,
        trip_id: UUID,
        start_stop_id: UUID,
        finish_stop_id: UUID,
    ) -> None:
        """
        Validate that start_stop_id and finish_stop_id exist in trip_stops for the given trip.
        Raises ServerException if stops are not found.
        """
        trip_stops_res = await self._session.execute(select(TripStop.stop_id).where(TripStop.trip_id == trip_id))
        valid_stop_ids = {row[0] for row in trip_stops_res.all()}

        if not valid_stop_ids:
            raise ServerException(message=f'Trip {trip_id} has no stops configured', status=400)

        if start_stop_id not in valid_stop_ids:
            raise ServerException(message=f'Start stop {start_stop_id} does not exist in this trip', status=400)

        if finish_stop_id not in valid_stop_ids:
            raise ServerException(message=f'Finish stop {finish_stop_id} does not exist in this trip', status=400)

    async def get_trip_stop_ids(self, trip_id: UUID) -> set[UUID]:
        """Get all stop IDs for a given trip."""
        trip_stops_res = await self._session.execute(select(TripStop.stop_id).where(TripStop.trip_id == trip_id))
        return {row[0] for row in trip_stops_res.all()}
