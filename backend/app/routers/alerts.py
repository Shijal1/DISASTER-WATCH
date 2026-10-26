from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.alert import Alert
from app.models.incident import Incident
from app.schemas.alert import AlertOut, AlertAcknowledge
from app.realtime.manager import manager
router = APIRouter(prefix="/api/alerts", tags=["alerts"])
@router.get("", response_model=list[AlertOut])
def list_alerts(status: str = "active", db: Session = Depends(get_db)):
    q = db.query(Alert)
    if status and status != "all":
        q = q.filter(Alert.status == status)
    return q.order_by(Alert.created_at.desc()).all()
@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
async def acknowledge_alert(alert_id: int, payload: AlertAcknowledge, db: Session = Depends(get_db)):
    alert = db.query(Alert).get(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    if alert.status != "active":
        raise HTTPException(400, f"Alert is already {alert.status}")
    alert.status = "acknowledged"
    alert.acknowledged_by = payload.acknowledged_by
    alert.acknowledged_at = datetime.utcnow()
    # If the alert is tied to an incident, mark the incident as acknowledged
    if alert.related_incident_id:
        inc = db.query(Incident).get(alert.related_incident_id)
        if inc and not inc.acknowledged_by:
            inc.acknowledged_by = payload.acknowledged_by
    db.commit()
    db.refresh(alert)
    await manager.broadcast("alert_acknowledged", {
        "alert_id": alert.alert_id,
        "acknowledged_by": alert.acknowledged_by,
    })
    return alert
@router.post("/{alert_id}/resolve", response_model=AlertOut)
async def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).get(alert_id)
    if not alert:
        raise HTTPException(404, "Alert not found")
    alert.status = "resolved"
    db.commit()
    db.refresh(alert)
    await manager.broadcast("alert_resolved", {"alert_id": alert.alert_id})
    return alert