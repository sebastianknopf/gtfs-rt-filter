"""HTTP adapter and configuration lifecycle; no GTFS-RT filtering logic."""
import asyncio
from contextlib import asynccontextmanager
import logging
from pathlib import Path
import signal

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from google.protobuf.message import DecodeError

from gtfsrtfilter.client import FeedClient
from gtfsrtfilter.config import Config, load_config
from gtfsrtfilter.service import FeedService

logger = logging.getLogger(__name__)


def create_app(config: Config, config_path: str | Path | None = None) -> FastAPI:
    """Create the HTTP application. Pass config_path to enable SIGHUP reloads."""
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0), follow_redirects=True) as client:
            feed_client = FeedClient(client)
            app.state.service = FeedService(config, feed_client)
            loop = asyncio.get_running_loop()
            signal_installed = False

            def reload_configuration() -> None:
                try:
                    updated = load_config(config_path)
                    if updated.app != config.app:
                        raise ValueError("app.host and app.port cannot change on reload; restart the service")
                    # Construct the entire new service (including GeoJSON filters)
                    # before switching references. In-flight requests retain the old one.
                    replacement = FeedService(updated, feed_client)
                    app.state.service = replacement
                    logger.info("Configuration reloaded successfully from %s", config_path)
                except Exception:
                    logger.exception("Configuration reload failed; previous configuration remains active")

            if config_path is not None and hasattr(signal, "SIGHUP"):
                try:
                    loop.add_signal_handler(signal.SIGHUP, reload_configuration)
                    signal_installed = True
                except (NotImplementedError, RuntimeError):
                    logger.warning("SIGHUP reload is not supported on this platform")
            try:
                yield
            finally:
                if signal_installed:
                    loop.remove_signal_handler(signal.SIGHUP)

    app = FastAPI(title="gtfs-rt-filter", docs_url=None, redoc_url=None,
                  openapi_url=None, lifespan=lifespan)

    @app.get("/{path:path}", include_in_schema=False)
    async def handle(request: Request, path: str):
        json_output = "json" in request.query_params or "debug" in request.query_params
        try:
            data = await request.app.state.service.process(request.url.path, json_output)
        except KeyError:
            return Response("Not Found", status_code=404, media_type="text/plain")
        except httpx.TimeoutException:
            return Response("Upstream request timed out", status_code=504, media_type="text/plain")
        except httpx.HTTPError:
            return Response("Upstream request failed", status_code=502, media_type="text/plain")
        except (DecodeError, ValueError):
            return Response("Invalid upstream GTFS-RT feed", status_code=502, media_type="text/plain")
        media_type = "application/json" if json_output else "application/x-protobuf"
        return Response(content=data, media_type=media_type, headers={"Cache-Control": "no-store"})

    return app
