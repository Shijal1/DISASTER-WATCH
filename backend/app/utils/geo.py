import json
import math


def circle_polygon(lat: float, lon: float, radius_km: float, points: int = 48) -> str:
    """Return a GeoJSON polygon approximating a circle of given radius."""
    coords = []
    for i in range(points):
        bearing = (i / points) * 2 * math.pi
        lat_off = (radius_km / 111.0) * math.cos(bearing)
        lon_off = (radius_km / (111.0 * math.cos(math.radians(lat)))) * math.sin(bearing)
        coords.append([lon + lon_off, lat + lat_off])
    coords.append(coords[0])

    geojson = {"type": "Polygon", "coordinates": [coords]}
    return json.dumps(geojson)


def offset_point(lat: float, lon: float, d_lat: float, d_lon: float) -> tuple[float, float]:
    return lat + d_lat, lon + d_lon


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))