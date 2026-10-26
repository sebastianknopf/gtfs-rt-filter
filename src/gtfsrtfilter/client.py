"""Asynchronous, uncached upstream transport."""

import httpx


class FeedClient:
    def __init__(self, client: httpx.AsyncClient):
        self.client = client

    async def fetch(self, url: str, authorization: str | None = None) -> bytes:
        """Fetch once, forwarding only the caller's Authorization header if present."""
        headers = {"Authorization": authorization} if authorization is not None else {}
        response = await self.client.get(url, headers=headers, follow_redirects=False)
        response.raise_for_status()
        return response.content
