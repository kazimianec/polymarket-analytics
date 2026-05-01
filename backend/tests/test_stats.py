"""Tests for stats overview endpoint."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services import stats as stats_service


class TestStatsOverviewReturnsExpectedStructure:
    """Tests for stats overview response structure."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_trending_markets(self) -> list[dict]:
        """Mock trending markets response."""
        return [
            {
                "id": "market-1",
                "question": "Will BTC reach 100k?",
                "volume": 5000000,
                "outcomePrices": {"Yes": "0.60", "No": "0.40"},
            },
            {
                "id": "market-2",
                "question": "Will ETH hit 5k?",
                "volume": 3000000,
                "outcomePrices": {"Yes": "0.45", "No": "0.55"},
            },
        ]

    @pytest.fixture
    def mock_tags_response(self) -> dict:
        """Mock tags API response."""
        return {
            "tags": [
                {"slug": "crypto", "label": "Crypto", "volume": 8000000},
                {"slug": "sports", "label": "Sports", "volume": 2000000},
                {"slug": "politics", "label": "Politics", "volume": 1000000},
            ]
        }

    @pytest.mark.asyncio
    async def test_stats_overview_returns_expected_structure(
        self,
        client: "PolymarketClient",
        mock_trending_markets: list[dict],
        mock_tags_response: dict,
    ) -> None:
        """Verify stats overview returns the expected response model."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_trending.return_value = mock_trending_markets
            mock_get.return_value = mock_tags_response

            result = await stats_service.get_stats_overview(client)

            # Verify structure
            assert "total_active_markets" in result
            assert "total_volume" in result
            assert "top_categories" in result
            assert "trending_markets" in result

            # Verify trending markets structure
            assert len(result["trending_markets"]) == 2
            trending = result["trending_markets"][0]
            assert hasattr(trending, "id")
            assert hasattr(trending, "question")
            assert hasattr(trending, "yes_price")
            assert hasattr(trending, "no_price")
            assert hasattr(trending, "volume")
            # Verify attribute access works
            assert trending.id == "market-1"
            assert trending.question == "Will BTC reach 100k?"

    @pytest.mark.asyncio
    async def test_stats_overview_calculates_totals_correctly(
        self,
        client: "PolymarketClient",
        mock_trending_markets: list[dict],
        mock_tags_response: dict,
    ) -> None:
        """Verify stats overview correctly sums volumes and counts markets."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_trending.return_value = mock_trending_markets
            mock_get.return_value = mock_tags_response

            result = await stats_service.get_stats_overview(client)

            # Verify total volume is sum of all market volumes
            expected_volume = 5000000 + 3000000
            assert result["total_volume"] == expected_volume

            # Verify top categories are sorted by volume
            assert len(result["top_categories"]) == 3
            volumes = [cat.volume for cat in result["top_categories"]]
            assert volumes == sorted(volumes, reverse=True)

    @pytest.mark.asyncio
    async def test_stats_overview_extracts_prices_correctly(
        self,
        client: "PolymarketClient",
        mock_trending_markets: list[dict],
        mock_tags_response: dict,
    ) -> None:
        """Verify yes/no prices are extracted correctly from outcomePrices."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_trending,
            patch.object(client, "_get", new_callable=AsyncMock) as mock_get,
        ):
            mock_trending.return_value = mock_trending_markets
            mock_get.return_value = mock_tags_response

            result = await stats_service.get_stats_overview(client)

            # First market: Yes=0.60, No=0.40
            first_market = result["trending_markets"][0]
            assert first_market.yes_price == 0.60
            assert first_market.no_price == 0.40
