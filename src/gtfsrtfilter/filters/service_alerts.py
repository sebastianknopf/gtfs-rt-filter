"""Filter individual alert selectors and discard alerts without selectors."""
from google.transit import gtfs_realtime_pb2
from gtfsrtfilter.filters.base import EntityFilter
from gtfsrtfilter.matching import groups, match_fields

class ServiceAlertsFilter(EntityFilter):
    def __init__(self, filters: list[dict]):
        self.criteria = groups(filters)

    def apply(self, feed: gtfs_realtime_pb2.FeedMessage) -> None:
        retained = []
        for entity in feed.entity:
            if not entity.HasField("alert"):
                continue
            alert = entity.alert
            if self.criteria:
                selectors = []
                for selector in alert.informed_entity:
                    values = {}
                    for key in ("agency_id", "route_id", "route_type", "stop_id"):
                        if selector.HasField(key):
                            values[key] = getattr(selector, key)
                    if selector.HasField("trip") and selector.trip.HasField("trip_id"):
                        values["trip_id"] = selector.trip.trip_id
                    if match_fields(values, self.criteria):
                        selectors.append(selector)
                del alert.informed_entity[:]
                alert.informed_entity.extend(selectors)
                if not selectors:
                    continue
            retained.append(entity)
        del feed.entity[:]
        feed.entity.extend(retained)
