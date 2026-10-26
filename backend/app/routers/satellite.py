from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.incident import Incident
from app.models.prediction import Prediction
from app.schemas.prediction import PredictionOut
from app.intelligence.satellite import (
    credentials_ok, get_access_token, layer_meta, wms_url, AVAILABLE_LAYERS
)
from app.intelligence.damage_detection import detect_flood
from app.realtime.manager import manager

router = APIRouter(prefix="/api/satellite", tags=["satellite"])


@router.get("/status")
async def status():
    ok = await credentials_ok()
    return {
        "credentials_configured": bool(ok),
        "wms_url": wms_url(),
        "layers": list(AVAILABLE_LAYERS.keys()),
    }


@router.get("/layers")
def layers():
    return layer_meta()


@router.get("/token")
async def token():
    t = await get_access_token()
    if not t:
        return {"error": "credentials not configured or invalid"}
    return {"access_token": t}


@router.post("/detect-flood/{incident_id}", response_model=PredictionOut)
async def detect_flood_endpoint(incident_id: int, db: Session = Depends(get_db)):
    inc = db.query(Incident).get(incident_id)
    if not inc:
        raise HTTPException(404, "Incident not found")

    result = await detect_flood(inc.latitude, inc.longitude)
    if "error" in result:
        raise HTTPException(400, result["error"])

    pred = Prediction(
        incident_id=incident_id,
        hazard_type="flood_detected",
        risk_level="DETECTED",
        geometry=result["geometry"],
        estimated_population=result["estimated_population"],
        recommended_action=(
            f"AI-detected flood extent: {result['flooded_area_km2']} km2 "
            f"({result['water_fraction']*100:.1f}% of analysed area), "
            f"estimated {result['estimated_population']} people affected. "
            f"Source: Sentinel-2 NDWI."
        ),
        is_estimate="AI_DETECTED",
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    await manager.broadcast("flood_detection_complete", {
        "incident_id": incident_id,
        "prediction_id": pred.prediction_id,
        "area_km2": result["flooded_area_km2"],
        "population": result["estimated_population"],
    })

    return pred