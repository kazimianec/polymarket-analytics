"""Tests for Polymarket API client service."""

import json
from unittest.mock import AsyncMock, patch

import pytest

from app.services.polymarket import PolymarketClient


class TestSearchMarkets:
    """Tests for search_markets method."""

    @pytest.fixture
    def client(self) -> PolymarketClient:
        return PolymarketClient()

    @pytest.fixture
    def mock_search_response(self) -> dict:
        """Sample Gamma API search response with double-encoded fields."""
        return {
            "events": [
                {
                    "id": "event-123",
                    "title": "Will ETH be above 4000 by Dec 2024?",
                    "description": "Test market description",
                    "volume": 1000000,
                    "outcomes": '["Yes", "No"]',  # double-encoded JSON string
                    "outcomePrices": '{"Yes": "0.45", "No": "0.55"}',  # double-encoded
                    "clobTokenIds": '["token-abc", "token-def"]',  # double-encoded
                }
            ]
        }

    @pytest.mark.asyncio
    async def test_search_markets_parses_response_correctly(
        self, client: PolymarketClient, mock_search_response: dict
    ) -> None:
        """Verify search_markets correctly parses the API response."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_search_response

            result = await client.search_markets("ETH")

            assert len(result) == 1
            event = result[0]
            assert event["id"] == "event-123"
            assert event["title"] == "Will ETH be above 4000 by Dec 2024?"
            # Verify double-encoded fields were parsed
            assert event["outcomes"] == ["Yes", "No"]
            assert event["outcomePrices"] == {"Yes": "0.45", "No": "0.55"}
            assert event["clobTokenIds"] == ["token-abc", "token-def"]

    @pytest.mark.asyncio
    async def test_search_markets_calls_correct_endpoint(
        self, client: PolymarketClient
    ) -> None:
        """Verify search_markets hits the Gamma API public-search endpoint."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"events": []}

            await client.search_markets("bitcoin")

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://gamma-api.polymarket.com"
            assert call_args[0][1] == "/public-search"
            assert call_args[1]["params"]["q"] == "bitcoin"


class TestGetMarketHistory:
    """Tests for get_market_history method."""

    @pytest.fixture
    def client(self) -> PolymarketClient:
        return PolymarketClient()

    @pytest.fixture
    def mock_history_response(self) -> list:
        """Sample CLOB API price history response."""
        return [
            {"t": 1704067200, "p": 0.45},
            {"t": 1704153600, "p": 0.48},
            {"t": 1704240000, "p": 0.46},
        ]

    @pytest.mark.asyncio
    async def test_get_market_history_returns_price_array(
        self, client: PolymarketClient, mock_history_response: list
    ) -> None:
        """Verify get_market_history returns properly structured price data."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_history_response

            result = await client.get_market_history("condition-123")

            assert isinstance(result, list)
            assert len(result) == 3
            assert result[0] == {"t": 1704067200, "p": 0.45}
            assert result[1] == {"t": 1704153600, "p": 0.48}
            assert result[2] == {"t": 1704240000, "p": 0.46}

    @pytest.mark.asyncio
    async def test_get_market_history_calls_correct_endpoint(
        self, client: PolymarketClient
    ) -> None:
        """Verify get_market_history hits the CLOB API prices-history endpoint."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = []

            await client.get_market_history("condition-abc", interval="1d", fidelity=50)

            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[0][0] == "https://clob.polymarket.com"
            assert call_args[0][1] == "/prices-history"
            assert call_args[1]["params"]["market"] == "condition-abc"
            assert call_args[1]["params"]["interval"] == "1d"


class TestDoubleEncodedFields:
    """Tests for double-encoded JSON string parsing."""

    @pytest.fixture
    def client(self) -> PolymarketClient:
        return PolymarketClient()

    @pytest.mark.asyncio
    async def test_double_encoded_fields_are_parsed(self, client: PolymarketClient) -> None:
        """Verify outcomePrices JSON string becomes a parsed list/dict."""
        raw_response = {
            "events": [
                {
                    "id": "event-456",
                    "title": "Will it rain tomorrow?",
                    "outcomes": '["Yes", "No"]',
                    "outcomePrices": '{"Yes": "0.60", "No": "0.40"}',
                    "clobTokenIds": '["clob-1", "clob-2"]',
                }
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = raw_response

            result = await client.search_markets("rain")

            event = result[0]
            # These should be parsed from JSON strings to actual Python types
            assert isinstance(event["outcomes"], list)
            assert event["outcomes"] == ["Yes", "No"]
            assert isinstance(event["outcomePrices"], dict)
            assert event["outcomePrices"] == {"Yes": "0.60", "No": "0.40"}
            assert isinstance(event["clobTokenIds"], list)
            assert event["clobTokenIds"] == ["clob-1", "clob-2"]


class TestGetTrendingMarkets:
    """Tests for get_trending_markets method."""

    @pytest.fixture
    def client(self) -> PolymarketClient:
        return PolymarketClient()

    @pytest.mark.asyncio
    async def test_get_trending_markets_returns_market_list(
        self, client: PolymarketClient
    ) -> None:
        """Verify get_trending_markets returns list of markets sorted by volume."""
        mock_response_data = {
            "markets": [
                {
                    "id": "market-1",
                    "question": "Will BTC reach 100k?",
                    "volume": 5000000,
                },
                {
                    "id": "market-2",
                    "question": "Will ETH merge happen?",
                    "volume": 3000000,
                },
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_data

            result = await client.get_trending_markets(limit=10)

            assert isinstance(result, list)
            assert len(result) == 2
            assert result[0]["id"] == "market-1"
            assert result[0]["volume"] == 5000000


class TestGetMarketDetail:
    """Tests for get_market_detail method."""

    @pytest.fixture
    def client(self) -> PolymarketClient:
        return PolymarketClient()

    @pytest.mark.asyncio
    async def test_get_market_detail_returns_market(
        self, client: PolymarketClient
    ) -> None:
        """Verify get_market_detail returns single market by ID."""
        mock_response_data = {
            "events": [
                {
                    "id": "market-detail-123",
                    "question": "Detailed market question",
                    "outcomes": '["Option A", "Option B"]',
                }
            ]
        }

        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response_data

            result = await client.get_market_detail("market-detail-123")

            assert result is not None
            assert result["id"] == "market-detail-123"
            assert isinstance(result["outcomes"], list)

    @pytest.mark.asyncio
    async def test_get_market_detail_returns_none_for_empty(
        self, client: PolymarketClient
    ) -> None:
        """Verify get_market_detail returns None when market not found."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = {"events": []}

            result = await client.get_market_detail("nonexistent")

            assert result is None
