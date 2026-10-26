"""GDACS multi-hazard alert feed adapter."""
from typing import Any
from app.feeds.base import FeedAdapter
class GDACSAdapter(FeedAdapter):
    name = "gdacs"
    source_label = "gdacs"
    URL = "https://www.gdacs.org/xml/rss.xml"
    # GDACS offers GeoJSON too; RSS is more robust
    async def fetch(self) -> list[dict[str, Any]]:
        r = await self._client.get(self.URL)
        r.raise_for_status()
        import xml.etree.ElementTree as ET
        root = ET.fromstring(r.text)
        items = []
        for item in root.iter("item"):
            items.append({
                "title": item.findtext("title"),
                "description": item.findtext("description"),
                "lat": item.findtext("{http://www.georss.org/georss}point") or "",
                "link": item.findtext("link"),
            })
        return items
    def normalise(self, raw: dict) -> dict | None:
        point = raw.get("lat") or ""
        parts = point.split()
        if len(parts) < 2:
            return None
        try:
            lat, lon = float(parts[0]), float(parts[1])
        except ValueError:
            return None
        title = (raw.get("title") or "").lower()
        if "earthquake" in title:
            dtype = "earthquake"
        elif "flood" in title:
            dtype = "flood"
        elif "cyclone" in title or "storm" in title:
            dtype = "cyclone"
        elif "fire" in title:
            dtype = "wildfire"
        elif "volcano" in title:
            dtype = "volcano"
        else:
            dtype = "other"
        return {
            "type": dtype,
            "location_name": raw.get("title"),
            "latitude": lat,
            "longitude": lon,
            "severity": "MODERATE",
            "description": raw.get("title") or "",
            "source": "gdacs",
            "verified_flag": True,
            "status": "active",
        }
