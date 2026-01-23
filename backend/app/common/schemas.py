from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

# Geographic coordinates types
Latitude = Annotated[float, Field(ge=-90, le=90, description='Latitude coordinate')]
Longitude = Annotated[float, Field(ge=-180, le=180, description='Longitude coordinate')]


class EntityModel(BaseModel):
    """Base model for entities with common fields."""

    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
