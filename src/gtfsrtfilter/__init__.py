"""GTFS-Realtime filtering service."""

try:
    from .version import __version__
except ImportError:
    # The generated module is only available after a setuptools-scm build.
    from importlib.metadata import PackageNotFoundError, version

    try:
        __version__ = version("gtfs-rt-filter")
    except PackageNotFoundError:
        __version__ = "unknown"
