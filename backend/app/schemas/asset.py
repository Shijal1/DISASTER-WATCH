from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class AssetBase(BaseModel):
    type: str
    label: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    availability: bool = True
    status: str = "idle"


class AssetCreate(AssetBase):
    pass


class AssetUpdate(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    availability: Optional[bool] = None
    status: Optional[str] = None
    assigned_incident_id: Optional[int] = None
    assigned_team_id: Optional[int] = None


class AssetOut(AssetBase):
    model_config = ConfigDict(from_attributes=True)

    asset_id: int
    assigned_incident_id: Optional[int] = None
    assigned_team_id: Optional[int] = None
    updated_at: datetime