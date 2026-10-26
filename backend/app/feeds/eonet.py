"""NASA EONET natural events feed adapter."""
from typing import Any
from app.feeds.base import FeedAdapter
CATEGORY_MAP = {
    "Wildfires": "wildfire",
    "Severe Storms": "storm",
    "Floods": "flood",
    "Volcanoes": "volcano",
    "Earthquakes": "earthquake",
    "Landslides": "landslide",
}
class EONETAdapter(FeedAdapter):
    name = "eonet"
    source_label = "eonet"
    URL = "https://eonet.gsfc.nasa.gov/api/v3/events?status=open&days=20"
    async def fetch(self) -> list[dict[str, Any]]:
        r = await self._client.get(self.URL)
        r.raise_for_status()
        return r.json().get("events", [])
    def normalise(self, raw: dict) -> dict | None:
        geoms = raw.get("geometry", [])
        if not geoms:
            return None
        latest = geoms[-1]
        coords = latest.get("coordinates", [])
        if not coords:
            return None
        if isinstance(coords[0], list):
            lon, lat = coords[0][0], coords[0][1]
        else:
            lon, lat = coords[0], coords[1]
        cats = raw.get("categories", [])
        cat_title = cats[0].get("title") if cats else "Unknown"
        dtype = CATEGORY_MAP.get(cat_title, "other")
        title = raw.get("title", "")
        return {
            "type": dtype,
            "location_name": title,
            "latitude": lat,
            "longitude": lon,
            "severity": "MODERATE",
            "description": f"[{cat_title}] {title}",
            "source": "eonet",
            "verified_flag": True,
            "status": "active",
        }