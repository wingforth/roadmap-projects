"""
Application configuration defaults.

This module exposes a small :class:`Config` used by the Flask application
factory. The values here are sane defaults for local development and can be
overridden by instance configuration or environment variables.
"""

import os


class Config:
    """Application configuration defaults.

    This class defines sane defaults for development. Override them with
    an ``instance/config.py`` file or environment variables in production.

    Attributes:
        WEATHER_API_KEY (str): VisualCrossing API key.
        CACHE_EXPIRE_TIME (int): Default cache TTL in seconds.
        REDIS_HOST, REDIS_PORT, REDIS_DB: Redis connection settings.
        RATELIMIT_DEFAULT (str): Flask-Limiter default rate limit string.
        RATELIMIT_STORAGE_URI (str): Storage backend for limiter.
    """

    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
    CACHE_EXPIRE_TIME = 12 * 60 * 60  # 12 hours
    # redis
    # REDIS_URL = "redis://localhost:6379/0"
    REDIS_HOST = "localhost"
    REDIS_PORT = 6379
    REDIS_DB = 0
    # ratelimiter
    RATELIMIT_DEFAULT = "10/minute, 30/hour, 100/day"
    RATELIMIT_STORAGE_URI = "redis://localhost:6379/0"
    RATELIMIT_STRATEGY = "fixed-window"
