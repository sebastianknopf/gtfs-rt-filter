"""Retain whole trip updates when all configured criteria match."""
from google.transit import gtfs_realtime_pb2
from gtfsrtfilter.filters.base import EntityFilter
from gtfsrtfilter.matching import groups, matches, match_fields

class TripUpdatesFilter(EntityFilter):
    def __init__(self, filters: list[dict]):
        self.criteria = groups(filters)

    def apply(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        retained = []
        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue
            update = entity.trip_update
            trip = update.trip
            values = {key: getattr(trip, key) for key in ("route_id", "trip_id") if trip.HasField(key)}
            scalar = {key: value for key, value in self.criteria.items() if key != "stop_id"}
            if not match_fields(values, scalar):
                continue
            if "stop_id" in self.criteria and not any(
                stop.HasField("stop_id") and matches(stop.stop_id, self.criteria["stop_id"])
                for stop in update.stop_time_update
            ):
                continue
            retained.append(entity)
        del feed.entity[:]
        feed.entity.extend(retained)
