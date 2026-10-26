from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident
from app.schemas.incident import IncidentCreate, IncidentUpdate, IncidentOut
from app.realtime.manager import manager
router = APIRouter(prefix="/api/incidents", tags=["incidents"])
@router.get("", response_model=list[IncidentOut])
def list_incidents(
    type: Optional[str] = None,
    severity: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(500, le=2000),
    db: Session = Depends(get_db),
):
    q = db.query(Incident)
    if type: q = q.filter(Incident.type == type)
    if severity: q = q.filter(Incident.severity == severity)
    if status: q = q.filter(Incident.status == status)
    return q.order_by(Incident.created_at.desc()).limit(limit).all()
@router.get("/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc: raise HTTPException(404, "Incident not found")
    return inc
@router.post("", response_model=IncidentOut, status_code=201)
def create_incident(payload: IncidentCreate, db: Session = Depends(get_db)):
    inc = Incident(**payload.model_dump())
    db.add(inc); db.commit(); db.refresh(inc)
    return inc
@router.patch("/{incident_id}", response_model=IncidentOut)
def update_incident(incident_id: int, payload: IncidentUpdate, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc: raise HTTPException(404, "Incident not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(inc, k, v)
    db.commit(); db.refresh(inc)
    return inc
@router.post("/{incident_id}/start-response", response_model=IncidentOut)
async def start_response(incident_id: int, operator: str = "operator", db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc: raise HTTPException(404, "Incident not found")
    if inc.status == "resolved":
        raise HTTPException(400, "Cannot start response on a resolved incident")
    inc.status = "responding"
    inc.responding_at = datetime.utcnow()
    if not inc.acknowledged_by:
        inc.acknowledged_by = operator
    db.commit(); db.refresh(inc)
    await manager.broadcast("incident_responding", {
        "incident_id": inc.incident_id,
        "operator": operator,
    })
    return inc
@router.post("/{incident_id}/resolve", response_model=IncidentOut)
async def resolve_incident(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc: raise HTTPException(404, "Incident not found")
    inc.status = "resolved"
    inc.resolved_at = datetime.utcnow()
    # Also resolve any active alerts attached to this incident
    for a in inc.alerts:
        if a.status != "resolved":
            a.status = "resolved"
    db.commit(); db.refresh(inc)
    await manager.broadcast("incident_resolved", {"incident_id": inc.incident_id})
    return inc