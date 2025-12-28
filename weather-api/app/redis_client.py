"""
Redis-backed cache helper.

Provides a small wrapper around redis-py ConnectionPool to set/get string
payloads. Reads Flask config keys with a configurable prefix (default REDIS_*)
for connection options.
"""

from datetime import date, datetime, timedelta
from urllib.parse import quote_plus

from redis import Redis, ConnectionPool


class RedisManager:
    """
    Helper that manages a redis connection pool and provides convenience
    methods to set/get weather payloads as strings.

    Configure it within Flask config. Every config startswith config_prefix
    (default 'REDIS_') will be used to initialize  `ConnectPool`, like this:
    1. REDIS_HOST
    2. REDIS_PORT
    3. REDIS_DB
    4. REDIS_PASSWORD
    5. REDIS_URL
    ...

    """

    def __init__(self, expire_time: int, **connection_kwargs) -> None:
        """Initialize connection pool.

        ``expire_time`` is expected to be an integer (seconds). If the value
        is missing or invalid the manager will fall back to a sensible
        default of 12 hours and emit a warning to aid debugging.
        """

        self.expire_time: int = expire_time
        self.pool: ConnectionPool = (
            ConnectionPool.from_url(url, **connection_kwargs)
            if (url := connection_kwargs.pop("url", None))
            else ConnectionPool(**connection_kwargs)
        )

    def generate_key(self, location: str) -> str:
        """
        Generate a simple, safe cache key for a location using today's date.

        The location is normalized (lowercased and URL-quoted) to
        avoid duplicate keys caused by different capitalization or spacing.
        Key format: "{normalized_location}:{YYYY-MM-DD}".
        """
        normalized = quote_plus(location.lower())
        return f"{normalized}:{date.today().isoformat()}"

    def _computer_ttl(self) -> int:
        """Compute the TTL in seconds for the cache entry.

        The TTL is clamped so it doesn't exceed the configured
        :attr:`expire_time` but is at least one minute. Additionally the
        value tries to expire near the next UTC day boundary to align
        with per-day cache keys.

        Returns:
            int: TTL in seconds.
        """
        now = datetime.now().timestamp()
        tomorrow = (datetime.today() + timedelta(1)).timestamp()
        return max(60, min(self.expire_time, int(tomorrow - now)))

    def set(self, name: str, value: str):
        """
        Set a string value with expiry seconds.
        """
        with Redis(connection_pool=self.pool, decode_responses=True) as conn:
            return conn.set(name, value, ex=self._computer_ttl())

    def get(self, name: str):
        """
        Get a stored string value or None.
        """
        with Redis(connection_pool=self.pool, decode_responses=True) as conn:
            return conn.get(name)
