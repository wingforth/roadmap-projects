"""app.views
=================

Flask route registration and small HTTP handlers for the Weather API.

This module exposes a single function :func:`register_routes` that accepts a
Flask application and registers the endpoints used by the service. Routes
are lightweight and rely on injected configuration (via ``app.config``)
and simple helpers for caching and the third-party weather client.

Docstring style in this module follows short descriptive summaries for each
public function to keep handler behavior easy to scan from code.
"""

from json import loads, dumps, JSONDecodeError

import redis
from flask import Flask, jsonify, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app import redis_client, weather_api


TWELVE_HOURS = 12 * 60 * 60


def register_routes(app: Flask) -> None:
    """Register HTTP routes on the Flask application.

    Reads configuration from :data:`app.config` (for example
    ``WEATHER_API_KEY`` and ``CACHE_EXPIRE_TIME``) and constructs a
    :class:`app.redis_client.RedisManager` instance. This function also
    initializes the Flask-Limiter instance for the registered routes.

    Args:
        app: Flask application to register routes on.

    Returns:
        None
    """

    weather_server = weather_api.VisualCrossingWeather(app.config.get("WEATHER_API_KEY", ""))

    # Parse CACHE_EXPIRE_TIME defensively
    expire_time = app.config.get("CACHE_EXPIRE_TIME", TWELVE_HOURS)
    try:
        expire_time = int(expire_time)
        if expire_time <= 0:
            raise ValueError("CACHE_EXPIRE_TIME must be a positive integer")
    except Exception as exc:
        app.logger.warning(
            "Invalid CACHE_EXPIRE_TIME=%r, falling back to default %s: %s",
            expire_time,
            TWELVE_HOURS,
            exc,
        )
        expire_time = TWELVE_HOURS

    redis_manager = redis_client.RedisManager(expire_time, **app.config.get_namespace("REDIS_"))
    limiter = Limiter(key_func=get_remote_address, app=app)

    def get_weather_data(location: str) -> dict:
        """Fetch weather for the given location using Redis cache when present.

        The function generates a stable cache key for the given location
        (per-day granularity), attempts to return a cached JSON payload
        when possible, and falls back to calling the upstream
        :class:`app.weather_api.VisualCrossingWeather` client.

        Any Redis errors are logged and ignored so the request still
        succeeds by fetching upstream data.

        Returns:
            dict: The provider JSON payload parsed as a Python dictionary.
        """
        # cache key is location + today's date
        # cache key is location + today's date
        key = redis_manager.generate_key(location)

        # Try to get from redis cache
        try:
            cached = redis_manager.get(key)
        except redis.RedisError as exc:
            # Log debug info but continue to fetch from upstream
            app.logger.warning("Redis get failed for key %s: %s", key, exc)
            cached = None

        if cached:
            # cached may be JSON string or bytes
            if isinstance(cached, (bytes, bytearray)):
                try:
                    cached = cached.decode()
                except UnicodeDecodeError:
                    cached = str(cached)
            try:
                if not isinstance(cached, (str, bytes, bytearray)):
                    cached = str(cached)
                return loads(cached)
            except JSONDecodeError:
                # Fall through to fetch fresh data from upstream
                pass

        # If failed to get from redis, request data from the weather API
        weather_data = weather_server.weather_forecast(location)
        try:
            # Store JSON string; cache key is location + date
            redis_manager.set(key, dumps(weather_data))
        except redis.RedisError as exc:
            # Cache failure should not fail request; log for visibility
            app.logger.warning("Redis set failed for key %s: %s", key, exc)

        return weather_data

    @app.route("/weather/<location>")
    def weather(location: str):
        """HTTP handler for GET /weather/<location>.

        Validates the path parameter and returns the provider JSON with
        a 200 status code on success. Maps internal exceptions to
        appropriate HTTP error responses (400/401/404/504/502).
        Returns:
            tuple: A Flask response and a numeric status code.
        """
        location = location.strip()
        if not location:
            return jsonify({"error": "location is required"}), 400

        try:
            weather = get_weather_data(location)
        except weather_api.InvalidParameterError:
            return jsonify({"error": f"Invalid location: {location}"}), 400
        except weather_api.InvalidApiKeyError:
            return jsonify({"error": f"Invalid weather API key: {location}"}), 401
        except weather_api.RequestTimeoutError as exc:
            app.logger.exception("Timeout while requesting weather API: %s", exc)
            return jsonify({"error": "Upstream connection timed out"}), 504
        except weather_api.RequestError as exc:
            app.logger.exception("Error occurred while requesting weather API: %s", exc)
            return jsonify({"error": "Internal Server Error"}), 500
        except weather_api.WeatherApiError as e:
            # Upstream or internal error
            return (
                jsonify({"error": "Failed to fetch weather from upstream", "detail": str(e)}),
                502,
            )

        return jsonify(weather), 200

    @app.route("/")
    @limiter.exempt
    def home():
        """Service information endpoint.

        Returns a tiny JSON object that can be used by health checks or
        service discovery.
        """
        return jsonify({"service": "weather-api", "version": "0.1"}), 200

    @app.route("/openapi.json")
    @limiter.exempt
    def openapi():
        """Return a minimal OpenAPI 3.0 JSON spec for the API.

        The spec is intentionally small and documents the main /weather
        endpoint plus the root info endpoint.
        """
        spec = {
            "openapi": "3.0.0",
            "info": {
                "title": "Weather API",
                "version": "0.1",
            },
            "paths": {
                "/weather": {
                    "get": {
                        "summary": "Get weather",
                        "parameters": [
                            {
                                "name": "location",
                                "in": "query",
                                "required": True,
                                "schema": {"type": "string"},
                            }
                        ],
                        "responses": {
                            "200": {"description": "OK"},
                            "400": {"description": "Bad Request"},
                            "401": {"description": "UNAUTHORIZED"},
                        },
                    }
                },
                "/": {"get": {"summary": "Service info"}},
            },
        }
        return jsonify(spec)

    @app.route("/docs")
    @limiter.exempt
    def docs():
        """Return a small ReDoc HTML page that loads /openapi.json.

        This is a convenience page for local development and manual API
        exploration.
        """
        script_src = "https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js"

        html = (
            "<!doctype html>\n"
            "<html>\n"
            "<head>\n"
            '  <meta charset="utf-8">\n'
            "  <title>API Docs</title>\n"
            "</head>\n"
            "<body>\n"
            '  <redoc spec-url="/openapi.json"></redoc>\n'
            f'  <script src="{script_src}"></script>\n'
            "</body>\n"
            "</html>"
        )
        return make_response(html, 200, {"Content-Type": "text/html; charset=utf-8"})

    @app.errorhandler(429)
    def ratelimit_handler(error):
        """JSON response for HTTP 429 (rate limit exceeded).

        Returns a JSON object with keys "error" and "detail" and the
        429 status code. The handler preserves any Retry-After header
        that Flask-Limiter may attach.
        """
        payload = {"error": "Rate limit exceeded", "detail": str(error)}
        return make_response(jsonify(payload), 429)
