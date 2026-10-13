"""HTTP adapter only: no GTFS-RT business logic."""
from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import Response
from google.protobuf.message import DecodeError
from gtfsrtfilter.client import FeedClient
from gtfsrtfilter.config import Config
from gtfsrtfilter.service import FeedService

def create_app(config: Config) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        async with httpx.AsyncClient(timeout=httpx.Timeout(20.0), follow_redirects=True) as client:
            app.state.service = FeedService(config, FeedClient(client))
            yield

    app = FastAPI(title="gtfs-rt-filter", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)

    async def handle(request: Request):
        json_output = "json" in request.query_params or "debug" in request.query_params
        try:
            data = await request.app.state.service.process(request.url.path, json_output)
        except httpx.TimeoutException:
            return Response("Upstream request timed out", status_code=504, media_type="text/plain")
        except httpx.HTTPError:
            return Response("Upstream request failed", status_code=502, media_type="text/plain")
        except (DecodeError, ValueError):
            return Response("Invalid upstream GTFS-RT feed", status_code=502, media_type="text/plain")
        media_type = "application/json" if json_output else "application/x-protobuf"
        return Response(content=data, media_type=media_type, headers={"Cache-Control": "no-store"})

    for entity in config.entities:
        app.add_api_route(entity.to, handle, methods=["GET"], include_in_schema=False)
    return app
