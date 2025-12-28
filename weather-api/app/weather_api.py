"""
VisualCrossingWeather service wrapper.

Provides a thin client for Visual Crossing Timeline API. The client returns
the parsed JSON response from the API
"""

from enum import IntEnum
from typing import NamedTuple
from urllib.parse import quote

import requests


class UnitGroup(NamedTuple):
    """Human-friendly unit symbols for a unit group returned by the API.

    Fields correspond to the following measurements that may appear in
    provider payloads: temperature, precipitation, snow, wind,
    visibility, pressure, solar radiation and solar energy.
    """

    temperature: str
    precipitation: str
    snow: str
    wind: str
    visibility: str
    pressure: str
    solar_radiation: str
    solar_energy: str


UNIT_GROUPS = {
    "metric": UnitGroup("°C", "mm", "cm", "km/h", "km", "hPa", "W/m²", "MJ/m²"),
    "base": UnitGroup("K", "mm", "cm", "m/s", "km", "mbar", "W/m²", "MJ/m²"),
    "us": UnitGroup("°F", "in", "in", "mi/h", "mi", "mbar", "W/m²", "MJ/m²"),
    "uk": UnitGroup("°C", "mm", "cm", "mi/h", "mi", "mbar", "W/m²", "MJ/m²"),
}

DEFAULT_UNIT_GROUP = "metric"  # one of metric, base, us, uk


class WeatherApiError(Exception):
    """Custom exception for weather service errors."""


class InvalidParameterError(WeatherApiError):
    """Invalid url parameters errors."""


class InvalidApiKeyError(WeatherApiError):
    """Invalid API key errors."""


class RequestError(WeatherApiError):
    """The request failed while trying to connect to the remote server."""


class RequestTimeoutError(RequestError):
    """The request timed out while trying to connect to the remote server."""


class HttpStatusCode(IntEnum):
    """Common HTTP status codes used for response handling."""

    OK = 200
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500


class VisualCrossingWeather:
    """Thin client for the VisualCrossing Timeline API.

    The client requires an API key at construction time and exposes one
    main method ``weather_forecast`` which returns parsed provider
    JSON. The object maintains a :class:`requests.Session` for connection
    reuse.

    Attributes:
        BASE_URL (str): Base endpoint for VisualCrossing timeline queries.
    """

    BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

    def __init__(self, api_key: str) -> None:
        """
        Initialize the client.

        Args:
            api_key: Visual Crossing API key.
        """
        if not api_key:
            raise RuntimeError("Missing weather API key.")
        self._query_params: dict[str, str] = {
            "key": api_key,
            "unitGroup": DEFAULT_UNIT_GROUP,
        }
        self.__session = requests.Session()

    @property
    def unit_group(self) -> UnitGroup:
        return UNIT_GROUPS[self._query_params["unitGroup"]]

    def _query_weather_data(self, url: str) -> dict:
        """Perform an HTTP GET and handle common HTTP error codes.

        Args:
            url: Fully formed URL (base + quoted location) for the request.

        Returns:
            dict: The parsed JSON response from the provider on success.

        Raises:
            WeatherApiError: On non-200 responses or request failures.
        """
        try:
            resp = self.__session.get(url=url, params=self._query_params, timeout=15)
        except requests.Timeout:
            raise RequestTimeoutError(f"Timeout while calling weather API {url}.")
        except requests.ConnectionError:
            raise RequestError(f"Connection error while calling weather API {url}")
        except requests.RequestException as e:
            raise RequestError(f"Unexpected requests error: {e}")

        match resp.status_code:
            case HttpStatusCode.OK:
                try:
                    return resp.json()
                except requests.JSONDecodeError as e:
                    raise WeatherApiError(f"Failed to decode weather response into json: {e}")
            case HttpStatusCode.BAD_REQUEST:
                raise InvalidParameterError(f"Invalid parameters provided for url {url}.")
            case HttpStatusCode.UNAUTHORIZED:
                raise InvalidApiKeyError("Unauthorized, invalid weather API key.")
            case HttpStatusCode.NOT_FOUND:
                raise WeatherApiError(f"Invalid weather API request endpoint {url}.")
            case HttpStatusCode.TOO_MANY_REQUESTS:
                raise WeatherApiError("Rate limit exceeded for weather API endpoint.")
            case HttpStatusCode.INTERNAL_SERVER_ERROR:
                raise WeatherApiError("Weather API failed to process the request.")
            case _:
                raise WeatherApiError(f"Unexpected weather API error: {resp.status_code} {resp.reason or ''}")

    def weather_forecast(self, location: str) -> dict:
        """Request a timeline forecast for ``location``.

        Args:
            location: Human readable location accepted by VisualCrossing
                (city, address, lat,long, etc.). The value is URL quoted.

        Returns:
            dict: The parsed provider JSON with an added ``unit_group``
                mapping containing units used in numeric fields.
        """
        url = f"{VisualCrossingWeather.BASE_URL}/{quote(location)}"
        weather_data = self._query_weather_data(url)
        # Add a small friendly unit_group mapping to help clients interpret
        # numeric fields (temperature, precipitation, etc.). This augments the
        # provider payload rather than replacing it.
        weather_data["unit_group"] = self.unit_group._asdict()
        return weather_data
