from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.incident import Incident
from app.models.alert import Alert
from app.schemas.sos import SOSCreate, SOSOut
from app.intelligence.sos_triage import classify
from app.intelligence.correlation import detect_and_flag
from app.realtime.manager import manager
router = APIRouter(prefix="/api/sos", tags=["sos"])
@router.post("", response_model=SOSOut, status_code=201)
async def submit_sos(payload: SOSCreate, db: Session = Depends(get_db)):
    triage = classify(payload.description)
    severity = triage["severity"]
    inc = Incident(
        type=payload.category,
        location_name=triage.get("candidate_location"),
        latitude=payload.latitude,
        longitude=payload.longitude,
        severity=severity,
        description=payload.description,
        source="citizen",
        verified_flag=False,
        status="active",
    )
    db.add(inc)
    db.commit()
    db.refresh(inc)
    alert = Alert(
        type="sos",
        severity="CRITICAL" if severity == "CRITICAL" else "WARNING",
        related_incident_id=inc.incident_id,
        message=f"New SOS ({severity}) at {payload.latitude:.3f},{payload.longitude:.3f} - {payload.category}: {payload.description[:80]}",
    )
    db.add(alert)
    db.commit()
    await manager.broadcast("sos_created", {
        "incident_id": inc.incident_id,
        "severity": severity,
        "category": payload.category,
        "evidence": triage["matched_evidence"],
        "latitude": inc.latitude,
        "longitude": inc.longitude,
    })
    await detect_and_flag(db, broadcaster=manager.broadcast)
    return SOSOut(
        severity=severity,
        matched_evidence=triage["matched_evidence"],
        candidate_location=triage.get("candidate_location"),
        incident_id=inc.incident_id,
        message="SOS received, incident created, correlation checked",
    )