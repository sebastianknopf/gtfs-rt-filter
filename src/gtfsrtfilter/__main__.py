"""Command-line entry point."""
import argparse
import uvicorn
from gtfsrtfilter.config import load_config
from gtfsrtfilter.server import create_app

def main() -> None:
    parser = argparse.ArgumentParser(description="On-demand GTFS-Realtime filtering proxy")
    parser.add_argument("--config", default="config.yaml", help="Path to YAML configuration")
    parser.add_argument("--reload", action="store_true", help="Restart server when source files change")
    args = parser.parse_args()
    config = load_config(args.config)
    if args.reload:
        # A factory with a stable import path is required for reload mode.
        import os
        os.environ["GTFS_RT_FILTER_CONFIG"] = args.config
        uvicorn.run("gtfsrtfilter.runtime:app_factory", factory=True, host=config.app.host, port=config.app.port, reload=True, reload_dirs=["src"])
    else:
        uvicorn.run(create_app(config), host=config.app.host, port=config.app.port)

if __name__ == "__main__":
    main()
