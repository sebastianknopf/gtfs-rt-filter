"""Filter vehicle positions by identifiers and geographic areas."""
from google.transit import gtfs_realtime_pb2
from gtfsrtfilter.filters.base import EntityFilter
from gtfsrtfilter.matching import groups, match_fields
from gtfsrtfilter.geo.polygons import load_geometry, contains

class VehiclePositionsFilter(EntityFilter):
    def __init__(self, filters: list[dict]):
        self.criteria = groups(filters)
        self.includes = [load_geometry(path) for path in self.criteria.pop("include", [])]
        self.excludes = [load_geometry(path) for path in self.criteria.pop("exclude", [])]

    def apply(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        retained = []
        for entity in feed.entity:
            if not entity.HasField("vehicle"):
                continue
            vehicle = entity.vehicle
            values = {}
            if vehicle.HasField("trip"):
                for key in ("route_id", "trip_id"):
                    if vehicle.trip.HasField(key):
                        values[key] = getattr(vehicle.trip, key)
            if vehicle.HasField("vehicle") and vehicle.vehicle.HasField("id"):
                values["vehicle_id"] = vehicle.vehicle.id
            if not match_fields(values, self.criteria):
                continue
            if self.includes or self.excludes:
                if not vehicle.HasField("position") or not vehicle.position.HasField("latitude") or not vehicle.position.HasField("longitude"):
                    continue
                lon, lat = vehicle.position.longitude, vehicle.position.latitude
                if self.includes and not any(contains(area, lon, lat) for area in self.includes):
                    continue
                if any(contains(area, lon, lat) for area in self.excludes):
                    continue
            retained.append(entity)
        del feed.entity[:]
        feed.entity.extend(retained)
