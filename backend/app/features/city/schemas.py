from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

Longitude = Annotated[float, Field(ge=-180, le=180)]
Latitude = Annotated[float, Field(ge=-90, le=90)]


class CityBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    longitude: Longitude
    latitude: Latitude


class CityCreate(CityBase):
    pass


class CityUpdate(CityBase):
    name: str | None = Field(None, min_length=1, max_length=255)
    longitude: Longitude | None = None
    latitude: Latitude | None = None


class CityRead(CityBase):
    id: UUID

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
