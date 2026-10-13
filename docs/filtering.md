# Filtering Behavior

Filters with the same key are OR-connected; distinct keys are AND-connected. `*` matches zero or more characters. A missing field never matches a configured filter. Without filters, all entities of the selected GTFS-RT type pass through.

## Service Alerts

Supported fields: `agency_id`, `route_id`, `route_type`, `stop_id`, `trip_id`. Each `Alert.informed_entity` selector is tested independently. Unmatched selectors are removed. If no selectors remain, the entire alert entity is removed. All other alert fields remain unchanged. Numeric `route_type` values are compared as strings for wildcard support.

## Trip Updates

Supported fields: `route_id`, `trip_id`, `stop_id`. Route and trip IDs come from the trip descriptor. `stop_id` matches if **any** `StopTimeUpdate` has a matching stop ID. When a trip matches, all its stop-time updates are preserved. No missing fields are inferred from static GTFS.

## Vehicle Positions

Supported fields: `route_id`, `trip_id`, `vehicle_id`, `include`, `exclude`. IDs are taken from the vehicle's trip descriptor or vehicle descriptor. GeoJSON include polygons accept positions inside or on their boundaries; exclude polygons reject them. If a spatial rule is configured, vehicles with no coordinates are rejected. Multiple include polygons are OR-connected; any exclude polygon rejects a position. Spatial excludes are applied after identifier matches.

Feed headers are retained; nonmatching FeedEntity entries are removed. The service does not modify GTFS-RT identifiers or enrich fields using GTFS Static.
