"""Asynchronous, uncached upstream transport."""
import httpx

class FeedClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def fetch(self, url: str) -> bytes:
        response = await self.client.get(url)
        response.raise_for_status()
        return response.content
