from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
class AlertBase(BaseModel):
    type: str
    severity: str = "INFO"
    related_incident_id: Optional[int] = None
    message: str
    status: str = "active"
class AlertCreate(AlertBase):
    pass
class AlertOut(AlertBase):
    model_config = ConfigDict(from_attributes=True)
    alert_id: int
    created_at: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    escalation_level: Optional[int] = 0
class AlertAcknowledge(BaseModel):
    acknowledged_by: str