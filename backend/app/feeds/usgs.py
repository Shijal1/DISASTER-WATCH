"""USGS earthquake feed adapter."""
from typing import Any
from app.feeds.base import FeedAdapter
class USGSAdapter(FeedAdapter):
    name = "usgs"
    source_label = "usgs"
    URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"
    async def fetch(self) -> list[dict[str, Any]]:
        r = await self._client.get(self.URL)
        r.raise_for_status()
        data = r.json()
        return data.get("features", [])
    def normalise(self, raw: dict) -> dict | None:
        props = raw.get("properties", {})
        geom = raw.get("geometry", {})
        coords = geom.get("coordinates", [])
        if len(coords) < 2:
            return None
        lon, lat = coords[0], coords[1]
        mag = props.get("mag") or 0
        if mag >= 6.0:
            severity = "CRITICAL"
        elif mag >= 5.0:
            severity = "HIGH"
        elif mag >= 4.0:
            severity = "MODERATE"
        else:
            severity = "LOW"
        place = props.get("place") or "unknown location"
        return {
            "type": "earthquake",
            "location_name": props.get("place") or "Unknown",
            "latitude": lat,
            "longitude": lon,
            "severity": severity,
            "description": f"M{mag} earthquake at {place}",
            "source": "usgs",
            "verified_flag": True,
            "status": "active",
        }