"""Polymarket API client service.

Wraps httpx calls to three Polymarket APIs:
- Gamma API: market discovery, search, browsing
- CLOB API: real-time prices, orderbook, price history
- Data API: trades, open interest
"""

import json
import logging
from typing import Any

import httpx

GAMMA_BASE = "https://gamma-api.polymarket.com"
CLOB_BASE = "https://clob.polymarket.com"
DATA_BASE = "https://data-api.polymarket.com"

logger = logging.getLogger(__name__)


class PolymarketHTTPError(Exception):
    """Raised when an HTTP request to Polymarket APIs fails."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _parse_double_encoded(value: Any) -> Any:
    """Parse a double-encoded JSON string field.

    Polymarket APIs return some fields as JSON-encoded strings
    (e.g., '"[\"Yes\", \"No\"]"' instead of '["Yes", "No"]').
    This function attempts to parse those strings.

    Args:
        value: The field value to parse. If string, attempts json.loads.
               Otherwise returns as-is.

    Returns:
        Parsed Python object (list, dict) or original value.
    """
    if isinstance(value, str):
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    return value


def _parse_event_fields(event: dict) -> dict:
    """Parse double-encoded fields in an event dict.

    Args:
        event: Raw event dict from Gamma API.

    Returns:
        Event dict with double-encoded fields parsed.
    """
    double_encoded_fields = ["outcomes", "outcomePrices", "clobTokenIds"]
    parsed = event.copy()
    for field in double_encoded_fields:
        if field in parsed:
            parsed[field] = _parse_double_encoded(parsed[field])
    return parsed


class PolymarketClient:
    """Async client for Polymarket public APIs.

    Provides methods to interact with Gamma API (market discovery),
    CLOB API (real-time prices), and Data API (trades).

    Example:
        client = PolymarketClient()
        markets = await client.get_trending_markets(limit=10)
        history = await client.get_market_history("condition-id")
    """

    async def _get(self, base_url: str, path: str, **kwargs) -> dict:
        """Make a GET request to a Polymarket API endpoint.

        Args:
            base_url: Base URL of the API (GAMMA_BASE, CLOB_BASE, or DATA_BASE).
            path: API endpoint path.
            **kwargs: Additional query parameters.

        Returns:
            Parsed JSON response dict.

        Raises:
            PolymarketHTTPError: On HTTP error status codes.
        """
        url = f"{base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, **kwargs)
            if response.status_code >= 400:
                raise PolymarketHTTPError(
                    f"Request to {url} failed with status {response.status_code}",
                    status_code=response.status_code,
                )
            return response.json()

    async def search_markets(self, query: str, limit: int = 20) -> list[dict]:
        """Search markets by keyword using Gamma API.

        Args:
            query: Search query string.
            limit: Maximum number of results to return.

        Returns:
            List of event dicts with nested markets, double-encoded fields parsed.
        """
        response = await self._get(
            GAMMA_BASE,
            "/public-search",
            params={"q": query, "limit": limit},
        )
        events = response.get("events", [])
        return [_parse_event_fields(event) for event in events]

    async def get_trending_markets(self, limit: int = 20) -> list[dict]:
        """Get top markets by volume (active, not closed) using Gamma API.

        Args:
            limit: Maximum number of markets to return.

        Returns:
            List of market dicts sorted by volume descending.
        """
        response = await self._get(
            GAMMA_BASE,
            "/markets",
            params={
                "limit": limit,
                "active": "true",
                "closed": "false",
                "order": "volume",
                "ascending": "false",
            },
        )
        return response.get("markets", [])

    async def get_market_history(
        self, condition_id: str, interval: str = "1d", fidelity: int = 50
    ) -> list[dict]:
        """Get price history for a market from CLOB API.

        Args:
            condition_id: Market condition ID.
            interval: Time interval for price points (e.g., "1d", "1h").
            fidelity: Resolution/fidelity of the price data (higher = more data).

        Returns:
            List of dicts with 't' (timestamp) and 'p' (price) keys.
        """
        response = await self._get(
            CLOB_BASE,
            "/prices-history",
            params={
                "market": condition_id,
                "interval": interval,
                "fidelity": fidelity,
            },
        )
        return response if isinstance(response, list) else []

    async def get_market_detail(self, market_id: str) -> dict | None:
        """Get single market by ID from Gamma API.

        Args:
            market_id: Unique market identifier.

        Returns:
            Market dict with parsed double-encoded fields, or None if not found.
        """
        response = await self._get(
            GAMMA_BASE,
            "/events",
            params={"id": market_id, "limit": 1},
        )
        events = response.get("events", [])
        if not events:
            return None
        return _parse_event_fields(events[0])

    async def get_recent_trades(
        self, condition_id: str, limit: int = 50
    ) -> list[dict]:
        """Get recent trades for a market from Data API.

        Args:
            condition_id: Market condition ID.
            limit: Maximum number of trades to return.

        Returns:
            List of trade dicts.
        """
        response = await self._get(
            DATA_BASE,
            "/trades",
            params={"market": condition_id, "limit": limit},
        )
        return response if isinstance(response, list) else []
