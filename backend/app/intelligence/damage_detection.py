"""F6: Satellite automated flood damage detection via Copernicus WMS."""
import io
import json
from datetime import datetime
from typing import Optional

import httpx
from PIL import Image

from app.intelligence.satellite import get_access_token, WMS_URL


BOX_SIZE_DEG = 0.5
IMAGE_PIXELS = 512
ASSUMED_DENSITY = 400


def _bbox_lonlat(lat: float, lon: float) -> tuple[float, float, float, float]:
    d = BOX_SIZE_DEG / 2
    return (lon - d, lat - d, lon + d, lat + d)


async def fetch_ndwi_tile(lat: float, lon: float) -> Optional[bytes]:
    token = await get_access_token()
    if not token:
        print("[damage] No token available")
        return None

    min_lon, min_lat, max_lon, max_lat = _bbox_lonlat(lat, lon)

    params = {
        "SERVICE": "WMS",
        "REQUEST": "GetMap",
        "VERSION": "1.1.1",
        "LAYERS": "NDWI",
        "SRS": "EPSG:4326",
        "BBOX": f"{min_lon},{min_lat},{max_lon},{max_lat}",
        "WIDTH": IMAGE_PIXELS,
        "HEIGHT": IMAGE_PIXELS,
        "FORMAT": "image/png",
        "TRANSPARENT": "true",
        "access_token": token,
    }

    async with httpx.AsyncClient(timeout=45.0) as client:
        r = await client.get(WMS_URL, params=params)
        print(f"[damage] WMS status: {r.status_code}")
        if r.status_code != 200:
            print(f"[damage] WMS body: {r.text[:500]}")
            return None
        return r.content


def analyse_ndwi_tile(png_bytes: bytes) -> dict:
    """
    Strict NDWI analysis. Only saturated blue pixels count as water.
    Requires the NDWI evalscript to output [0, 76, 255, 255] for water.
    """
    img = Image.open(io.BytesIO(png_bytes)).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    water_pixels = 0
    total_valid = 0
    min_x, min_y = w, h
    max_x, max_y = 0, 0

    for y in range(h):
        for x in range(w):
            r, g, b, a = pixels[x, y]
            if a < 100:
                continue
            total_valid += 1
            # Strict water: saturated blue only
            if b > 180 and r < 80 and g < 150:
                water_pixels += 1
                if x < min_x: min_x = x
                if y < min_y: min_y = y
                if x > max_x: max_x = x
                if y > max_y: max_y = y

    if total_valid == 0:
        return {"water_fraction": 0, "bounds_px": None, "total_valid": 0}

    return {
        "water_fraction": water_pixels / total_valid,
        "water_pixels": water_pixels,
        "total_valid": total_valid,
        "bounds_px": (min_x, min_y, max_x, max_y) if water_pixels > 0 else None,
    }


def pixels_to_geojson(lat: float, lon: float, bounds_px: tuple[int, int, int, int]) -> str:
    min_x, min_y, max_x, max_y = bounds_px
    d = BOX_SIZE_DEG / 2

    min_lat, max_lat = lat - d, lat + d
    min_lon, max_lon = lon - d, lon + d

    def px_to_lon(px: int) -> float:
        return min_lon + (px / IMAGE_PIXELS) * (max_lon - min_lon)

    def px_to_lat(py: int) -> float:
        return max_lat - (py / IMAGE_PIXELS) * (max_lat - min_lat)

    lons = [px_to_lon(min_x), px_to_lon(max_x)]
    lats = [px_to_lat(max_y), px_to_lat(min_y)]

    polygon = [
        [lons[0], lats[0]],
        [lons[1], lats[0]],
        [lons[1], lats[1]],
        [lons[0], lats[1]],
        [lons[0], lats[0]],
    ]
    return json.dumps({"type": "Polygon", "coordinates": [polygon]})


def estimate_area_and_population(water_fraction: float) -> tuple[float, int]:
    box_km = BOX_SIZE_DEG * 111.0
    box_area_km2 = box_km * box_km
    flooded_km2 = water_fraction * box_area_km2
    population = int(flooded_km2 * ASSUMED_DENSITY)
    return round(flooded_km2, 2), population


async def detect_flood(lat: float, lon: float) -> dict:
    print(f"[damage] Fetching NDWI for {lat:.3f},{lon:.3f}")
    png = await fetch_ndwi_tile(lat, lon)
    if not png:
        return {"error": "NDWI fetch failed"}

    analysis = analyse_ndwi_tile(png)
    if not analysis["bounds_px"]:
        return {"error": "No water detected in area"}

    geometry = pixels_to_geojson(lat, lon, analysis["bounds_px"])
    area_km2, population = estimate_area_and_population(analysis["water_fraction"])

    return {
        "geometry": geometry,
        "water_fraction": round(analysis["water_fraction"], 4),
        "flooded_area_km2": area_km2,
        "estimated_population": population,
        "water_pixels": analysis["water_pixels"],
        "analysed_at": datetime.utcnow().isoformat(),
        "source": "sentinel-2-ndwi",
    }