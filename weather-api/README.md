# Weather API — JSON HTTP service (VisualCrossing)

This repository provides a small JSON HTTP API that fetches weather data
from the VisualCrossing Timeline API, caches provider responses in Redis,
and applies rate limiting via `flask-limiter`.

The application exposes a simple `/weather/<location>` endpoint that returns
the provider's JSON payload augmented with a small `unit_group` helper so
clients can interpret numeric fields (temperature, precipitation, etc.).

Key ideas:

- Keep the service lightweight and API-only (no client-side JavaScript).
- Cache responses per-location and per-day to reduce upstream calls.
- Apply per-IP rate limits to protect the upstream API and the service.

## Quick Start (development)

Prerequisites

- Python (the repo uses an `uv` wrapper to run a managed interpreter)
- Optional: Redis for caching and shared limiter storage

Run locally

1. Install dependencies in the managed environment (using `uv` if available):

```powershell
uv sync            # optional project wrapper step
uv run python -m pip install -r requirements.txt
uv run python -m pip install -e .
```

2. Set the VisualCrossing API key and any optional config (env or instance config):

```powershell
$env:WEATHER_API_KEY = "<your_visualcrossing_api_key>"
$env:RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"  # optional
```

3. Start the app:

```powershell
uv run python run.py
```

Visit `http://127.0.0.1:5000/` for service info and `http://127.0.0.1:5000/docs`
for the small ReDoc-based documentation UI.

## Configuration

Configuration can come from `instance/config.py` or environment variables.
Important keys (available on `app.config`):

- `WEATHER_API_KEY` (required): VisualCrossing API key.
- `CACHE_EXPIRE_TIME`: TTL in seconds for cached weather responses (int).
- `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`, or `REDIS_URL`: Redis connection.
- `RATELIMIT_DEFAULT`: default rate limit (e.g. `5/minute`).
- `RATELIMIT_STORAGE_URI`: storage backend for flask-limiter (e.g. Redis).

The app falls back to sensible defaults for development when values are
missing, but you must provide `WEATHER_API_KEY` to make real requests.


## API Endpoints

- `GET /` — service info JSON: `{ "service": "weather-api", "version": "0.1" }`
- `GET /weather/<location>` — get weather for `location` (provider JSON + `unit_group`).
- `GET /openapi.json` — OpenAPI 3.0 spec describing the API.
- `GET /docs` — ReDoc UI that loads `/openapi.json`.

### Example curl requests

**Success:**
```sh
curl -s "http://127.0.0.1:5000/weather/London" | jq
```

**Rate limit exceeded:**
```sh
for i in {1..12}; do curl -s "http://127.0.0.1:5000/weather/London"; done
# The last request will return:
# {"error": "Rate limit exceeded", "detail": "429 Too Many Requests: ..."}
```

**Error (bad request):**
```sh
curl -s "http://127.0.0.1:5000/weather/" # returns {"error": "location is required"}
```

**Upstream error (API key missing):**
```sh
curl -s "http://127.0.0.1:5000/weather/London" # returns {"error": "Invalid weather API key: London"}
```

### OpenAPI spec quick reference

The `/openapi.json` endpoint returns a minimal OpenAPI 3.0 spec:

```json
{
  "openapi": "3.0.0",
  "info": { "title": "Weather API", "version": "0.1" },
  "paths": {
    "/weather": {
      "get": {
        "summary": "Get weather",
        "parameters": [
          { "name": "location", "in": "query", "required": true, "schema": {"type": "string"} }
        ],
        "responses": {
          "200": {"description": "OK"},
          "400": {"description": "Bad Request"},
          "401": {"description": "UNAUTHORIZED"}
        }
      }
    },
    "/": { "get": { "summary": "Service info" } }
  }
}
```

You can view the interactive docs at [http://127.0.0.1:5000/docs](http://127.0.0.1:5000/docs).

## Testing

Tests use `pytest` and `responses` to mock HTTP calls. Run tests using the
project-managed Python:

```powershell
uv run python -m pytest -q
```

The test suite includes cases for successful fetch and cache behavior,
upstream errors and timeouts, and rate-limit behavior.

## Production notes

- Use Redis (`RATELIMIT_STORAGE_URI`) for limiter storage when running
  multiple worker processes so rate limits are shared across workers.
- When deploying behind a proxy, use `werkzeug.middleware.proxy_fix.ProxyFix`
  so `get_remote_address()` returns the correct client IP.
- Keep the VisualCrossing API key secret (env vars or instance config).
