from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ResourceBase(BaseModel):
    type: str
    quantity: int = 0
    unit: str = "units"
    minimum_threshold: int = 0


class ResourceCreate(ResourceBase):
    camp_id: int


class ResourceUpdate(BaseModel):
    quantity: Optional[int] = None
    minimum_threshold: Optional[int] = None


class ResourceOut(ResourceBase):
    model_config = ConfigDict(from_attributes=True)

    resource_id: int
    camp_id: int
    updated_at: datetime