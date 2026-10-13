# Configuration

Create `config.yaml` from `config.example.yaml` and start with `gtfs-rt-filter --config config.yaml`.

`app.host` and `app.port` control the listening address. Each `entities` item defines a `type`, an upstream HTTP `from` URL, a local `to` path, and optional `filters`.

Supported entity types: `service-alerts`, `trip-updates`, `vehicle-positions`. Local paths must be unique. Filter entries must contain exactly one key. Unknown filters and incompatible entity/filter combinations fail validation at startup.

GeoJSON paths for `include` and `exclude` are read once at startup and must refer to valid Polygon or MultiPolygon geometry (or Feature/FeatureCollection wrappers). Restart the service after editing configuration or polygon files. Paths are resolved relative to the process working directory; absolute paths are recommended for production.

The service does not cache feed responses. Each HTTP request triggers one upstream request. Connection pooling within httpx does not cache response bodies.
