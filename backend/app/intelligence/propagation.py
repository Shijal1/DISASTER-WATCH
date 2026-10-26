"""
Algorithm 2 — Parameterised geographic propagation.
Produces four tiered impact zones around a hazard centre.
These are decision-support ESTIMATES, not validated forecasts.
"""
from datetime import datetime, timedelta
from typing import Optional

from app.utils.geo import offset_point, circle_polygon

# Propagation parameters per hazard type: (radius_km, velocity_kmh)
PROPAGATION_PARAMS = {
    "flood":      [(5, 3),   (15, 6),   (30, 12),  (60, 24)],
    "earthquake": [(10, 999), (25, 999), (50, 999), (100, 999)],  # instantaneous
    "wildfire":   [(3, 5),   (10, 10),  (25, 20),  (50, 35)],
    "cyclone":    [(20, 15), (50, 30),  (100, 50), (200, 80)],
    "landslide":  [(2, 999), (8, 999),  (20, 999), (40, 999)],
    "storm":      [(10, 20), (30, 40),  (60, 60),  (120, 90)],
    "other":      [(5, 10),  (15, 20),  (30, 30),  (60, 50)],
}

TIER_LABELS = ["CORE", "HIGH", "MEDIUM", "LOW"]

ASSUMED_DENSITY_PER_KM2 = 400  # people per km² (indicative)

ACTION_MAP = {
    ("flood", "CORE"): "Immediate evacuation and rescue deployment",
    ("flood", "HIGH"): "Prepare evacuation, mobilise boats and rescue teams",
    ("flood", "MEDIUM"): "Issue advisory, pre-position relief supplies",
    ("flood", "LOW"): "Monitor water levels and rainfall forecasts",
    ("earthquake", "CORE"): "Search and rescue; structural triage",
    ("earthquake", "HIGH"): "Damage assessment and medical triage",
    ("earthquake", "MEDIUM"): "Shelter assessment, clear debris corridors",
    ("earthquake", "LOW"): "Monitor aftershocks; inspect infrastructure",
    ("wildfire", "CORE"): "Evacuate, deploy firefighting assets",
    ("wildfire", "HIGH"): "Evacuation readiness; establish firebreaks",
    ("wildfire", "MEDIUM"): "Advisory; smoke-health warning",
    ("wildfire", "LOW"): "Monitor wind and humidity",
}


def _action_for(hazard: str, tier: str) -> str:
    return ACTION_MAP.get((hazard, tier), "Follow standard operating procedure")


def generate_zones(
    hazard_type: str,
    latitude: float,
    longitude: float,
) -> list[dict]:
    """
    Returns a list of 4 tier dicts, each with:
      tier, risk_level, geometry (GeoJSON string), estimated_arrival,
      estimated_population, recommended_action, is_estimate
    """
    params = PROPAGATION_PARAMS.get(hazard_type, PROPAGATION_PARAMS["other"])
    zones = []
    now = datetime.utcnow()

    for idx, (radius_km, velocity_kmh) in enumerate(params):
        tier = TIER_LABELS[idx]

        if velocity_kmh >= 999:
            arrival = None  # instantaneous
        else:
            hours = radius_km / velocity_kmh
            arrival = now + timedelta(hours=hours)

        area_km2 = 3.14159 * (radius_km ** 2)
        population = int(area_km2 * ASSUMED_DENSITY_PER_KM2)

        geometry = circle_polygon(latitude, longitude, radius_km)

        zones.append({
            "tier": tier,
            "risk_level": tier,
            "geometry": geometry,
            "estimated_arrival": arrival,
            "estimated_population": population,
            "recommended_action": _action_for(hazard_type, tier),
            "is_estimate": "ESTIMATE",
        })

    return zones