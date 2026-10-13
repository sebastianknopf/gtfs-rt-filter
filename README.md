# gtfs-rt-filter

[![Tests](https://github.com/sebastianknopf/gtfs-rt-filter/actions/workflows/tests.yml/badge.svg)](https://github.com/sebastianknopf/gtfs-rt-filter/actions/workflows/tests.yml)

An asynchronous, on-demand GTFS-Realtime filtering proxy powered by FastAPI, httpx and Protocol Buffers. Every incoming request fetches the upstream feed again. No feed caching or scheduled polling is performed.

## Development

Requires Python 3.11+ and a Git checkout with its `.git` directory. Package versions are derived from Git tags using `setuptools-scm`; `src/gtfsrtfilter/version.py` is generated during builds and ignored by Git.

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
The installer preserves an existing configuration. **Deploy from a complete Git clone, not a GitHub source ZIP:** the installer copies `.git` into `/opt/gtfs-rt-filter` so `setuptools-scm` can calculate the version.

See the [complete systemd deployment guide](docs/systemd.md) for installation,
permissions, enabling the service, logs, upgrades, and removal.

## Tests and Releases

GitHub Actions runs tests on pushes, pull requests, and version tags. Push a tag
(e.g. `0.1.0`) to run the release workflow, which builds wheel/source archives
and attaches them to a GitHub Release. The repository needs GitHub Actions
permission to create releases (`contents: write`). See
[Versioning and Releases](docs/versioning.md).

## Documentation

- [Configuration](docs/configuration.md)
- [Filtering Rules](docs/filtering.md)
- [HTTP API](docs/http-api.md)
- [Systemd Deployment](docs/systemd.md)
- [Versioning and Releases](docs/versioning.md)

## License

This project is licensed under the Apache 2.0 license. See [LICENSE.md](LICENSE.md) for the full license text.
