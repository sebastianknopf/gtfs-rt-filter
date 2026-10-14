"""Regression tests for configuration reload without restarting Uvicorn."""
import asyncio

import pytest

from gtfsrtfilter.config import load_config
from gtfsrtfilter.server import create_app


@pytest.mark.asyncio
async def test_sighup_reloads_routes_and_keeps_last_good_config(tmp_path, monkeypatch):
    path = tmp_path / "config.yaml"

    def write_config(destination):
        path.write_text(
            "app:\n  host: 127.0.0.1\n  port: 8080\n"
            "entities:\n  - type: trip-updates\n"
            "    from: http://127.0.0.1:8081/rt/trip-updates.pbf\n"
            f"    to: {destination}\n",
            encoding="utf-8",
        )

    write_config("/old")
    app = create_app(load_config(path), config_path=path)
    loop = asyncio.get_running_loop()
    callbacks = {}
    monkeypatch.setattr(loop, "add_signal_handler", lambda sig, fn: callbacks.setdefault(sig, fn))
    monkeypatch.setattr(loop, "remove_signal_handler", lambda sig: callbacks.pop(sig, None))

    async with app.router.lifespan_context(app):
        assert "/old" in app.state.service.routes
        callback = next(iter(callbacks.values()))
        write_config("/new")
        callback()
        assert "/new" in app.state.service.routes
        assert "/old" not in app.state.service.routes
        path.write_text("invalid: [", encoding="utf-8")
        callback()
        assert "/new" in app.state.service.routes
