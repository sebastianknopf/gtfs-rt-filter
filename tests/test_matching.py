from gtfsrtfilter.matching import groups, match_fields

def test_or_and_missing():
    rules = groups([{"route_id": "a*"}, {"route_id": "b*"}, {"trip_id": "1"}])
    assert match_fields({"route_id": "abc", "trip_id": "1"}, rules)
    assert not match_fields({"route_id": "abc"}, rules)
