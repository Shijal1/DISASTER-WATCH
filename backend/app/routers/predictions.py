from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.prediction import Prediction
from app.models.incident import Incident
from app.schemas.prediction import PredictionOut
from app.intelligence.propagation import generate_zones
from app.intelligence.allocation import assign_nearest
from app.realtime.manager import manager
router = APIRouter(prefix="/api/predictions", tags=["predictions"])
@router.get("/{incident_id}", response_model=list[PredictionOut])
def get_predictions(incident_id: int, db: Session = Depends(get_db)):
    return db.query(Prediction).filter(Prediction.incident_id == incident_id).all()
@router.post("/generate", response_model=list[PredictionOut])
async def generate_predictions(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    db.query(Prediction).filter(Prediction.incident_id == incident_id).delete()
    db.commit()
    zones = generate_zones(inc.type, inc.latitude, inc.longitude)
    created = []
    for z in zones:
        p = Prediction(
            incident_id=incident_id,
            hazard_type=inc.type,
            risk_level=z["risk_level"],
            geometry=z["geometry"],
            estimated_arrival=z["estimated_arrival"],
            estimated_population=z["estimated_population"],
            recommended_action=z["recommended_action"],
            is_estimate=z["is_estimate"],
        )
        db.add(p)
        created.append(p)
    db.commit()
    for p in created:
        db.refresh(p)
    await manager.broadcast("predictions_generated", {
        "incident_id": incident_id,
        "zones": len(created),
    })
    return created
@router.post("/{incident_id}/auto-assign")
async def auto_assign(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")
    result = assign_nearest(db, inc)
    await manager.broadcast("asset_assigned", {
        "incident_id": incident_id,
        **result,
    })
    return result
