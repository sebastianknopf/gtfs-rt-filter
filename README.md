# gtfs-rt-filter

An asynchronous, on-demand GTFS-Realtime filtering proxy powered by FastAPI, httpx and Protocol Buffers. Every incoming request fetches the upstream feed again. No feed caching or scheduled polling is performed.

## Development

Requires Python 3.11+.

```sh
python -m venv venv
. venv/bin/activate
pip install -e '.[dev]'
cp config.example.yaml config.yaml
gtfs-rt-filter --config config.yaml --reload
```

On Windows, activate with `venv\Scripts\activate` instead.

Run tests with `pytest`.

## Production

For guided installation or updates on a systemd-based Linux host, run:

```sh
./deploy.sh
```

Use `./deploy.sh --yes` for noninteractive installation or add `--link` to
create an optional command symlink under `/usr/local/bin`.
The installer preserves an existing configuration.

See the [complete systemd deployment guide](docs/systemd.md) for installation,
permissions, enabling the service, logs, upgrades, and removal.

## Documentation

- [Configuration](docs/configuration.md)
- [Filtering Rules](docs/filtering.md)
- [HTTP API](docs/http-api.md)
- [Systemd Deployment](docs/systemd.md)

## License

This project is licensed under the Apache 2.0 license. See [LICENSE.md](LICENSE.md) for the full license text.
