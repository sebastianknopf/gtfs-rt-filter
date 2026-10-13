"""Load GeoJSON geometry and test whether coordinates are covered."""
import json
from pathlib import Path
from shapely.geometry import Point, shape
from shapely.ops import unary_union

def load_geometry(filename: str):
    data = json.loads(Path(filename).read_text(encoding="utf-8"))
    if data.get("type") == "FeatureCollection":
        geometries = [shape(item["geometry"]) for item in data["features"] if item.get("geometry")]
    elif data.get("type") == "Feature":
        geometries = [shape(data["geometry"])]
    else:
        geometries = [shape(data)]
    if not geometries or any(g.geom_type not in {"Polygon", "MultiPolygon"} or not g.is_valid for g in geometries):
        raise ValueError(f"Invalid polygon GeoJSON: {filename}")
    return unary_union(geometries)

def contains(geometry, longitude: float, latitude: float) -> bool:
    return geometry.covers(Point(longitude, latitude))
