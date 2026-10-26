"""F1: SOS-to-feed correlation for emerging unverified event detection."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.incident import Incident
from app.models.alert import Alert
from app.utils.geo import haversine_km
CLUSTER_RADIUS_KM = 25.0
CLUSTER_WINDOW_HOURS = 2
MIN_REPORTS_FOR_CLUSTER = 3
OFFICIAL_SOURCES = {"usgs", "eonet", "gdacs"}
def find_emerging_clusters(db: Session) -> list[dict]:
    """
    Find clusters of citizen reports that have no official feed event nearby.
    Returns a list of cluster dicts: {lat, lng, count, types, incident_ids}
    """
    cutoff = datetime.utcnow() - timedelta(hours=CLUSTER_WINDOW_HOURS)
    citizens = (
        db.query(Incident)
        .filter(Incident.source == "citizen")
        .filter(Incident.created_at >= cutoff)
        .all()
    )
    if len(citizens) < MIN_REPORTS_FOR_CLUSTER:
        return []
    # Simple greedy clustering
    used = set()
    clusters = []
    for i, seed in enumerate(citizens):
        if i in used:
            continue
        group = [seed]
        used.add(i)
        for j, other in enumerate(citizens):
            if j in used:
                continue
            if haversine_km(seed.latitude, seed.longitude,
                            other.latitude, other.longitude) <= CLUSTER_RADIUS_KM:
                group.append(other)
                used.add(j)
        if len(group) < MIN_REPORTS_FOR_CLUSTER:
            continue
        types = {g.type for g in group}
        if len(types) > 1:
            continue  # mixed-type cluster, skip
        # Check if an official event exists nearby
        has_official = False
        for g in group:
            cutoff2 = datetime.utcnow() - timedelta(hours=6)
            nearby_official = (
                db.query(Incident)
                .filter(Incident.source.in_(OFFICIAL_SOURCES))
                .filter(Incident.created_at >= cutoff2)
                .filter(Incident.type == g.type)
                .all()
            )
            for off in nearby_official:
                if haversine_km(g.latitude, g.longitude,
                                off.latitude, off.longitude) <= CLUSTER_RADIUS_KM * 2:
                    has_official = True
                    break
            if has_official:
                break
        if has_official:
            continue
        clusters.append({
            "latitude": sum(g.latitude for g in group) / len(group),
            "longitude": sum(g.longitude for g in group) / len(group),
            "count": len(group),
            "type": group[0].type,
            "incident_ids": [g.incident_id for g in group],
        })
    return clusters
async def detect_and_flag(db: Session, broadcaster=None) -> list[dict]:
    """
    Run correlation. Creates EMERGING_UNVERIFIED incidents and alerts.
    Returns newly created clusters.
    """
    clusters = find_emerging_clusters(db)
    created = []
    for c in clusters:
        # Dedup: has this cluster already produced an emerging incident?
        existing = (
            db.query(Incident)
            .filter(Incident.source == "correlation")
            .filter(Incident.type == c["type"])
            .filter(Incident.latitude.between(c["latitude"] - 0.05, c["latitude"] + 0.05))
            .filter(Incident.longitude.between(c["longitude"] - 0.05, c["longitude"] + 0.05))
            .first()
        )
        if existing:
            continue
        inc = Incident(
            type=c["type"],
            location_name=f"Emerging cluster ({c['count']} reports)",
            latitude=c["latitude"],
            longitude=c["longitude"],
            severity="HIGH",
            description=(
                f"Emerging unverified event: {c['count']} citizen reports "
                f"for {c['type']} within {CLUSTER_RADIUS_KM}km over "
                f"{CLUSTER_WINDOW_HOURS}h, with no official feed event nearby. "
                f"Incident IDs: {c['incident_ids']}"
            ),
            source="correlation",
            verified_flag=False,
            status="active",
        )
        db.add(inc)
        db.commit()
        db.refresh(inc)
        alert = Alert(
            type="emerging_event",
            severity="CRITICAL",
            related_incident_id=inc.incident_id,
            message=(
                f"EMERGING unverified {c['type']} detected: {c['count']} SOS reports "
                f"clustered but no official source confirms. Requires verification."
            ),
        )
        db.add(alert)
        db.commit()
        c["incident_id"] = inc.incident_id
        created.append(c)
        if broadcaster:
            await broadcaster("emerging_event", {
                "incident_id": inc.incident_id,
                "type": inc.type,
                "latitude": inc.latitude,
                "longitude": inc.longitude,
                "count": c["count"],
            })
    return created