from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.utils.geo import haversine_km

# Which asset types are compatible with which incidents
COMPATIBILITY = {
    "flood":      ["boat", "helicopter", "rescue_team", "ambulance"],
    "earthquake": ["ambulance", "helicopter", "fire_truck", "rescue_team"],
    "wildfire":   ["fire_truck", "helicopter", "ambulance"],
    "cyclone":    ["helicopter", "boat", "ambulance", "rescue_team"],
    "landslide":  ["rescue_team", "ambulance", "helicopter"],
    "storm":      ["ambulance", "rescue_team", "fire_truck"],
    "other":      ["ambulance", "rescue_team"],
}


def assign_nearest(db: Session, incident) -> dict:
    """
    Greedy nearest-available assignment.
    Returns {assigned: bool, asset_id, distance_km, reason}
    """
    compatible = COMPATIBILITY.get(incident.type, COMPATIBILITY["other"])

    candidates = (
        db.query(Asset)
        .filter(Asset.availability == True)               # noqa: E712
        .filter(Asset.type.in_(compatible))
        .all()
    )

    if not candidates:
        return {"assigned": False, "reason": "no compatible available asset"}

    scored = [
        (haversine_km(a.latitude, a.longitude, incident.latitude, incident.longitude), a)
        for a in candidates
    ]
    scored.sort(key=lambda x: x[0])
    distance, chosen = scored[0]

    chosen.assigned_incident_id = incident.incident_id
    chosen.availability = False
    chosen.status = "assigned"
    db.commit()
    db.refresh(chosen)

    return {
        "assigned": True,
        "asset_id": chosen.asset_id,
        "asset_type": chosen.type,
        "distance_km": round(distance, 2),
        "reason": "nearest compatible available asset",
    }