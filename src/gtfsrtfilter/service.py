"""Orchestrate fetching, decoding, filtering and serialization."""
import asyncio
from google.protobuf.message import DecodeError
from gtfsrtfilter.client import FeedClient
from gtfsrtfilter.config import Config
from gtfsrtfilter.filters.service_alerts import ServiceAlertsFilter
from gtfsrtfilter.filters.trip_updates import TripUpdatesFilter
from gtfsrtfilter.filters.vehicle_positions import VehiclePositionsFilter
from gtfsrtfilter.serialization import decode, encode

FILTERS = {
    "service-alerts": ServiceAlertsFilter,
    "trip-updates": TripUpdatesFilter,
    "vehicle-positions": VehiclePositionsFilter,
}

class FeedService:
    def __init__(self, config: Config, client: FeedClient):
        self.client = client
        self.routes = {entity.to: (str(entity.source), FILTERS[entity.type](entity.filters)) for entity in config.entities}

    async def process(self, path: str, json_output: bool, authorization: str | None = None) -> bytes:
        url, filter_instance = self.routes[path]
        payload = await self.client.fetch(url, authorization=authorization)
        return await asyncio.to_thread(self._transform, payload, filter_instance, json_output)

    @staticmethod
    def _transform(payload: bytes, filter_instance, json_output: bool) -> bytes:
        feed = decode(payload)
        filter_instance.apply(feed)
        return encode(feed, json_output)
