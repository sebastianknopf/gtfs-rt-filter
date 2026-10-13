# Versioning and GitHub Releases

`gtfs-rt-filter` uses `setuptools-scm` to derive package versions from Git
metadata. The build generates `src/gtfsrtfilter/version.py` automatically.
Do not edit or commit this file; it is listed in `.gitignore`.

## Development

Use a full Git clone with its `.git` directory:

```sh
git clone https://github.com/sebastianknopf/gtfs-rt-filter.git
cd gtfs-rt-filter
python3 -m venv venv
. venv/bin/activate
python -m pip install -e '.[dev]'
pytest
```

The clone URL is an example; replace it with your repository URL. For
production deployment, `deploy.sh` copies the Git metadata to `/opt` before
installing the Python package. A source ZIP without `.git` is not supported by
the deployment script. The installed wheel does not need `.git` at runtime.

## Create a Release

Create and push a version tag, for example:

```sh
git tag 0.1.0
git push origin 0.1.0
```

The `Tests` workflow runs `pytest` on pull requests, main branch pushes, and
version tags. The `Release` workflow independently runs the tests, builds a
wheel and source distribution, checks their metadata, and publishes both as
assets on a GitHub Release associated with the pushed tag. It does not publish
to PyPI.

Ensure Actions are enabled and the repository permits the release workflow
to create releases. The workflow requests `contents: write` for this purpose.

The README test badge uses the example repository path
`sebastianknopf/gtfs-rt-filter`; update it if your GitHub repository differs.
