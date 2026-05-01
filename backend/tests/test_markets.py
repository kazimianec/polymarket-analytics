"""Tests for markets endpoints."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services import markets as markets_service


class TestTrendingMarketsReturnsPaginatedMarkets:
    """Tests for GET /api/v1/markets/trending endpoint."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_trending_response(self) -> list[dict]:
        """Mock trending markets response from Gamma API.

        Uses outcomePrices format as returned by PolymarketClient after parsing.
        """
        return [
            {
                "id": "market-1",
                "question": "Will BTC reach 100k by end of 2024?",
                "outcomePrices": {"Yes": "0.65", "No": "0.35"},
                "volume": 5000000.0,
                "liquidity": 1000000.0,
                "category": "crypto",
                "endDate": "2024-12-31T00:00:00Z",
                "active": True,
                "closed": False,
            },
            {
                "id": "market-2",
                "question": "Will ETH surpass 5k in 2024?",
                "outcomePrices": {"Yes": "0.45", "No": "0.55"},
                "volume": 3000000.0,
                "liquidity": 800000.0,
                "category": "crypto",
                "endDate": "2024-12-31T00:00:00Z",
                "active": True,
                "closed": False,
            },
        ]

    @pytest.mark.asyncio
    async def test_trending_returns_paginated_markets(
        self,
        client: "PolymarketClient",
        mock_trending_response: list[dict],
    ) -> None:
        """Verify trending endpoint returns paginated markets with correct structure."""
        with patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending:
            mock_trending.return_value = mock_trending_response

            result = await markets_service.get_trending_markets(client, limit=20, offset=0)

            # Verify structure
            assert "markets" in result
            assert "total" in result
            assert "has_more" in result

            # Verify markets list
            assert len(result["markets"]) == 2
            market = result["markets"][0]
            assert hasattr(market, "id")
            assert hasattr(market, "question")
            assert hasattr(market, "yes_price")
            assert hasattr(market, "no_price")
            assert hasattr(market, "volume")
            assert hasattr(market, "liquidity")
            assert hasattr(market, "category")
            assert hasattr(market, "end_date")
            assert hasattr(market, "active")
            assert hasattr(market, "closed")

            # Verify attribute access
            assert market.id == "market-1"
            assert market.question == "Will BTC reach 100k by end of 2024?"
            assert market.yes_price == 0.65
            assert market.no_price == 0.35
            assert market.volume == 5000000.0
            assert market.liquidity == 1000000.0
            assert market.category == "crypto"
            assert market.active is True
            assert market.closed is False

    @pytest.mark.asyncio
    async def test_trending_pagination_calculates_has_more(
        self,
        client: "PolymarketClient",
        mock_trending_response: list[dict],
    ) -> None:
        """Verify has_more is True when there are more markets than returned."""
        with patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending:
            # Return full list (2 markets), but request only 1 per page
            mock_trending.return_value = mock_trending_response

            result = await markets_service.get_trending_markets(client, limit=1, offset=0)

            # has_more should be True because total=2 > limit=1
            assert result["has_more"] is True
            assert len(result["markets"]) == 1

    @pytest.mark.asyncio
    async def test_trending_no_more_results(
        self,
        client: "PolymarketClient",
        mock_trending_response: list[dict],
    ) -> None:
        """Verify has_more is False when all markets are returned."""
        with patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending:
            mock_trending.return_value = mock_trending_response

            result = await markets_service.get_trending_markets(client, limit=10, offset=0)

            assert result["has_more"] is False
            assert result["total"] == 2


class TestMarketDetailReturnsFullInfo:
    """Tests for GET /api/v1/markets/{market_id} endpoint."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_market_detail(self) -> dict:
        """Mock single market detail response.

        Uses outcomePrices format as returned by PolymarketClient after parsing.
        """
        return {
            "id": "test-market-123",
            "question": "Will BTC reach 100k by end of 2024?",
            "description": "This market resolves to Yes if BTC reaches $100,000 USD on any major exchange before Dec 31, 2024.",
            "outcomePrices": {"Yes": "0.65", "No": "0.35"},
            "volume": 5000000.0,
            "liquidity": 1000000.0,
            "category": "crypto",
            "endDate": "2024-12-31T00:00:00Z",
            "outcomes": ["Yes", "No"],
            "active": True,
            "closed": False,
            "conditionId": "cond-123",
            "clobTokenIds": ["token-1", "token-2"],
        }

    @pytest.mark.asyncio
    async def test_market_detail_returns_full_info(
        self,
        client: "PolymarketClient",
        mock_market_detail: dict,
    ) -> None:
        """Verify market detail returns all fields."""
        with patch.object(client, "get_market_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = mock_market_detail

            result = await markets_service.get_market_detail(client, "test-market-123")

            # Verify all fields are present
            assert hasattr(result, "id")
            assert hasattr(result, "question")
            assert hasattr(result, "description")
            assert hasattr(result, "yes_price")
            assert hasattr(result, "no_price")
            assert hasattr(result, "volume")
            assert hasattr(result, "liquidity")
            assert hasattr(result, "category")
            assert hasattr(result, "end_date")
            assert hasattr(result, "outcomes")
            assert hasattr(result, "active")
            assert hasattr(result, "closed")
            assert hasattr(result, "condition_id")
            assert hasattr(result, "clob_token_ids")

            # Verify values
            assert result.id == "test-market-123"
            assert result.question == "Will BTC reach 100k by end of 2024?"
            assert result.description == "This market resolves to Yes if BTC reaches $100,000 USD on any major exchange before Dec 31, 2024."
            assert result.yes_price == 0.65
            assert result.no_price == 0.35
            assert result.volume == 5000000.0
            assert result.liquidity == 1000000.0
            assert result.category == "crypto"
            assert result.end_date == "2024-12-31T00:00:00Z"
            assert result.outcomes == ["Yes", "No"]
            assert result.active is True
            assert result.closed is False
            assert result.condition_id == "cond-123"
            assert result.clob_token_ids == ["token-1", "token-2"]

    @pytest.mark.asyncio
    async def test_market_detail_not_found(
        self,
        client: "PolymarketClient",
    ) -> None:
        """Verify market detail returns None for non-existent market."""
        with patch.object(client, "get_market_detail", new_callable=AsyncMock) as mock_detail:
            mock_detail.return_value = None

            result = await markets_service.get_market_detail(client, "non-existent")

            assert result is None


class TestMarketHistoryReturnsTimestampedPrices:
    """Tests for GET /api/v1/markets/{market_id}/history endpoint."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_history_response(self) -> list[dict]:
        """Mock price history response from CLOB API."""
        return [
            {"t": 1704067200, "p": 0.55},
            {"t": 1704153600, "p": 0.58},
            {"t": 1704240000, "p": 0.62},
            {"t": 1704326400, "p": 0.60},
            {"t": 1704412800, "p": 0.65},
        ]

    @pytest.mark.asyncio
    async def test_market_history_returns_timestamped_prices(
        self,
        client: "PolymarketClient",
        mock_history_response: list[dict],
    ) -> None:
        """Verify market history returns correctly structured price data."""
        with patch.object(client, "get_market_history", new_callable=AsyncMock) as mock_history:
            mock_history.return_value = mock_history_response

            result = await markets_service.get_market_history(
                client, "cond-123", interval="1d", fidelity=50
            )

            # Verify it's a Pydantic model with history attribute
            assert hasattr(result, "history")
            assert len(result.history) == 5

            # Verify each price point
            first_point = result.history[0]
            assert hasattr(first_point, "timestamp")
            assert hasattr(first_point, "price")

            assert first_point.timestamp == 1704067200
            assert first_point.price == 0.55

    @pytest.mark.asyncio
    async def test_market_history_empty_response(
        self,
        client: "PolymarketClient",
    ) -> None:
        """Verify market history handles empty response gracefully."""
        with patch.object(client, "get_market_history", new_callable=AsyncMock) as mock_history:
            mock_history.return_value = []

            result = await markets_service.get_market_history(
                client, "cond-123", interval="1d", fidelity=50
            )

            assert hasattr(result, "history")
            assert len(result.history) == 0
