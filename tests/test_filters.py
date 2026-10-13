from google.transit import gtfs_realtime_pb2 as pb
from gtfsrtfilter.filters.service_alerts import ServiceAlertsFilter
from gtfsrtfilter.filters.trip_updates import TripUpdatesFilter
from gtfsrtfilter.serialization import encode, decode

def test_alert_selector_filter():
    feed = pb.FeedMessage(); feed.header.gtfs_realtime_version = '2.0'
    entity = feed.entity.add(); entity.id = 'a'
    entity.alert.informed_entity.add().agency_id = 'match'
    entity.alert.informed_entity.add().agency_id = 'other'
    ServiceAlertsFilter([{'agency_id':'match'}]).apply(feed)
    assert len(feed.entity[0].alert.informed_entity) == 1

def test_trip_preserves_all_stops():
    feed = pb.FeedMessage(); feed.header.gtfs_realtime_version = '2.0'
    entity = feed.entity.add(); entity.id = 't'; entity.trip_update.trip.trip_id = '1'
    entity.trip_update.stop_time_update.add().stop_id = 'match'
    entity.trip_update.stop_time_update.add().stop_id = 'other'
    TripUpdatesFilter([{'stop_id':'match'}]).apply(feed)
    assert len(feed.entity[0].trip_update.stop_time_update) == 2
    assert b'\n  "header"' in encode(feed, True)
    assert decode(encode(feed, False)).header.gtfs_realtime_version == '2.0'
