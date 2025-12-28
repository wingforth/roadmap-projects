import re

import pytest
import responses

from app import create_app
from app import redis_client


class FakeRedisManager:
    def __init__(self, expire_time: int = 3600, **kwargs):
        self.store = {}
        self.set_calls = 0
        self.get_calls = 0

    def generate_key(self, location: str) -> str:
        return f"{location}:2025-11-17"

    def set(self, name: str, value: str):
        self.set_calls += 1
        self.store[name] = value
        return True

    def get(self, name: str):
        self.get_calls += 1
        return self.store.get(name)


@pytest.fixture
def app(monkeypatch):
    # replace RedisManager with a fake to avoid real Redis dependency
    monkeypatch.setattr(redis_client, "RedisManager", FakeRedisManager)

    # Create app with testing config and in-memory limiter storage
    from app import config

    config.Config.WEATHER_API_KEY = "test-key"
    config.Config.RATELIMIT_STORAGE_URI = "memory://"
    config.Config.RATELIMIT_DEFAULT = "2/minute"

    app = create_app()
    app.testing = True
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@responses.activate
def test_weather_success_and_cache(client, monkeypatch):
    # Mock the external VisualCrossing API
    responses.add(
        responses.GET,
        re.compile(r"https://weather\.visualcrossing\.com/.*"),
        json={"days": [], "resolvedAddress": "London, UK"},
        status=200,
    )

    # First request should fetch from upstream and set cache
    rv = client.get("/weather/London")
    assert rv.status_code == 200
    data = rv.get_json()
    assert data["resolvedAddress"] == "London, UK"
    # ensure unit_group was injected
    assert "unit_group" in data

    # Second request should hit the fake redis cache (no extra upstream call)
    rv2 = client.get("/weather/London")
    assert rv2.status_code == 200
    assert responses.calls.__len__() == 1


@responses.activate
def test_upstream_500_returns_502(client):
    responses.add(
        responses.GET,
        re.compile(r"https://weather\.visualcrossing\.com/.*"),
        json={"error": "boom"},
        status=500,
    )

    rv = client.get("/weather/Nowhere")
    assert rv.status_code == 502
    data = rv.get_json()
    assert "error" in data


@responses.activate
def test_upstream_timeout_returns_504(client):
    import requests

    responses.add(
        responses.GET,
        re.compile(r"https://weather\.visualcrossing\.com/.*"),
        body=requests.Timeout(),
    )

    rv = client.get("/weather/TimeoutTown")
    assert rv.status_code == 504


def test_rate_limit_exceeded(client):
    # RATELIMIT_DEFAULT set to 2/min in fixture; 3rd request should 429
    _ = client.get("/weather/London")
    _ = client.get("/weather/London")
    rv3 = client.get("/weather/London")

    # The third request should be rate-limited
    assert rv3.status_code == 429
    data = rv3.get_json()
    assert data.get("error") == "Rate limit exceeded"
