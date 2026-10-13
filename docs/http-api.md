# HTTP API

Each configured `to` path exposes a GET endpoint. Requests fetch the corresponding upstream `from` URL and return a newly filtered GTFS-RT `FeedMessage`.

```sh
curl -o filtered.pbf http://localhost:8080/filtered/rt/trip-updates.pbf
curl 'http://localhost:8080/filtered/rt/trip-updates.pbf?json'
curl 'http://localhost:8080/filtered/rt/trip-updates.pbf?debug'
```

By default the response is Protocol Buffers with `Content-Type: application/x-protobuf`. The presence of `json` or `debug` as a query parameter, regardless of its value (including an empty value or `false`), selects pretty-printed canonical protobuf JSON with `Content-Type: application/json`. JSON uses the protobuf serializer's standard JSON field naming. Both modes filter identically.

Upstream HTTP errors produce `502 Bad Gateway`; timeouts produce `504 Gateway Timeout`; invalid upstream protobuf data produces `502 Bad Gateway`. Responses include `Cache-Control: no-store`.
