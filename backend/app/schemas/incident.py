from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
class IncidentBase(BaseModel):
    type: str
    location_name: Optional[str] = None
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    severity: str = "LOW"
    description: Optional[str] = None
    source: str = "citizen"
    verified_flag: bool = False
    status: str = "active"
class IncidentCreate(IncidentBase):
    pass
class IncidentUpdate(BaseModel):
    severity: Optional[str] = None
    status: Optional[str] = None
    verified_flag: Optional[bool] = None
    description: Optional[str] = None
    acknowledged_by: Optional[str] = None
class IncidentOut(IncidentBase):
    model_config = ConfigDict(from_attributes=True)
    incident_id: int
    created_at: datetime
    acknowledged_by: Optional[str] = None
    responding_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None