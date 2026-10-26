# HTTP API

Each configured `to` path exposes a GET endpoint. Requests fetch the corresponding upstream `from` URL and return a newly filtered GTFS-RT `FeedMessage`.

```sh
curl -o filtered.pbf http://localhost:8080/filtered/rt/trip-updates.pbf
curl 'http://localhost:8080/filtered/rt/trip-updates.pbf?json'
curl 'http://localhost:8080/filtered/rt/trip-updates.pbf?debug'
```

By default the response is Protocol Buffers with `Content-Type: application/x-protobuf`. The presence of `json` or `debug` as a query parameter, regardless of its value (including an empty value or `false`), selects pretty-printed canonical protobuf JSON with `Content-Type: application/json`. JSON uses the protobuf serializer's standard JSON field naming. Both modes filter identically.

Upstream HTTP errors produce `502 Bad Gateway`; timeouts produce `504 Gateway Timeout`; invalid upstream protobuf data produces `502 Bad Gateway`. Responses include `Cache-Control: no-store`.

## Upstream HTTP Basic Authentication

The proxy does not authenticate clients or store credentials. If the incoming
request includes an `Authorization` header (for example, `Basic ...`), that
header is forwarded unchanged to the configured upstream URL. Requests without
this header are forwarded without credentials. This works identically for
protobuf and `?json` / `?debug` responses.

If the upstream responds with `401 Unauthorized`, the proxy returns `401` and
forwards its `WWW-Authenticate` challenge, allowing a browser or HTTP client to
prompt for credentials. Upstream `403 Forbidden` is returned as `403`.
Other upstream HTTP errors return `502 Bad Gateway`.

Upstream redirects are **not followed**; a redirect response is treated as an
upstream error (`502`) to avoid forwarding credentials to another destination.
Credentials are not logged by the application. Use HTTPS for client-to-proxy
and proxy-to-upstream traffic whenever Basic credentials travel over a network.

```sh
curl -u username:password \
  'https://filter.example/filtered/rt/trip-updates.pbf?json'
```
