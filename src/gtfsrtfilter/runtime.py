"""Importable app factory for Uvicorn reload."""
import os
from gtfsrtfilter.config import load_config
from gtfsrtfilter.server import create_app

def app_factory():
    return create_app(load_config(os.environ.get("GTFS_RT_FILTER_CONFIG", "config.yaml")))
