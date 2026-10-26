"""HTTP Basic authentication is transparently relayed to upstream feeds."""

import httpx
import pytest
from google.transit import gtfs_realtime_pb2 as pb

from gtfsrtfilter.client import FeedClient
from gtfsrtfilter.config import Config
from gtfsrtfilter.server import create_app


def config():
    return Config.model_validate({"entities": [{
        "type": "trip-updates", "from": "https://upstream.example/feed.pbf",
        "to": "/filtered/feed.pbf",
    }]})


@pytest.mark.asyncio
@pytest.mark.parametrize("suffix", ["", "?json", "?debug"])
async def test_basic_auth_challenge_and_success(suffix):
    seen = []
    feed = pb.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"

    def upstream(request):
        seen.append(request)
        if request.headers.get("authorization") != "Basic dXNlcjpwYXNz":
            return httpx.Response(401, headers={"WWW-Authenticate": 'Basic realm="Transit"'})
        return httpx.Response(200, content=feed.SerializeToString())

    app = create_app(config())
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as source:
            app.state.service.client = FeedClient(source)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                denied = await client.get("/filtered/feed.pbf" + suffix)
                assert denied.status_code == 401
                assert denied.headers["www-authenticate"] == 'Basic realm="Transit"'
                assert "authorization" not in seen[-1].headers
                accepted = await client.get("/filtered/feed.pbf" + suffix,
                                            headers={"Authorization": "Basic dXNlcjpwYXNz"})
                assert accepted.status_code == 200
                assert seen[-1].headers["authorization"] == "Basic dXNlcjpwYXNz"
                if suffix:
                    assert accepted.headers["content-type"].startswith("application/json")
                else:
                    assert accepted.content == feed.SerializeToString()


@pytest.mark.asyncio
async def test_forbidden_is_forwarded_and_redirects_are_not_followed():
    requests = []

    def upstream(request):
        requests.append(request)
        if "authorization" in request.headers:
            return httpx.Response(302, headers={"Location": "https://other.example/"})
        return httpx.Response(403)

    app = create_app(config())
    async with app.router.lifespan_context(app):
        async with httpx.AsyncClient(transport=httpx.MockTransport(upstream)) as source:
            app.state.service.client = FeedClient(source)
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url="http://test") as client:
                assert (await client.get("/filtered/feed.pbf")).status_code == 403
                assert (await client.get("/filtered/feed.pbf", headers={"Authorization": "Basic abc"})).status_code == 502
    assert len(requests) == 2
