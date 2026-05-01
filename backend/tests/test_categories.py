"""Tests for category endpoints."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services import categories as categories_service


class TestCategoryListReturnsCategories:
    """Tests for GET /api/v1/stats/categories endpoint."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_tags_response(self) -> dict:
        """Mock tags API response with category data."""
        return {
            "tags": [
                {
                    "slug": "crypto",
                    "label": "Crypto",
                    "volume": 8000000,
                    "marketCount": 150,
                },
                {
                    "slug": "sports",
                    "label": "Sports",
                    "volume": 5000000,
                    "marketCount": 200,
                },
                {
                    "slug": "politics",
                    "label": "Politics",
                    "volume": 3000000,
                    "marketCount": 100,
                },
            ]
        }

    @pytest.mark.asyncio
    async def test_category_list_returns_expected_structure(
        self,
        client: "PolymarketClient",
        mock_tags_response: dict,
    ) -> None:
        """Verify categories list returns the expected response structure."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tags_response

            result = await categories_service.get_categories(client)

            # Verify top-level structure
            assert "categories" in result
            assert isinstance(result["categories"], list)

            # Verify each category has required fields
            assert len(result["categories"]) == 3
            first_category = result["categories"][0]
            assert hasattr(first_category, "slug")
            assert hasattr(first_category, "label")
            assert hasattr(first_category, "volume")
            assert hasattr(first_category, "market_count")

    @pytest.mark.asyncio
    async def test_category_list_sorted_by_volume(
        self,
        client: "PolymarketClient",
        mock_tags_response: dict,
    ) -> None:
        """Verify categories are sorted by volume descending."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tags_response

            result = await categories_service.get_categories(client)

            # Verify sorted by volume descending
            volumes = [cat.volume for cat in result["categories"]]
            assert volumes == sorted(volumes, reverse=True)

    @pytest.mark.asyncio
    async def test_category_list_extracts_fields_correctly(
        self,
        client: "PolymarketClient",
        mock_tags_response: dict,
    ) -> None:
        """Verify category fields are extracted correctly."""
        with patch.object(client, "_get", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_tags_response

            result = await categories_service.get_categories(client)

            # First category should be crypto (highest volume)
            first = result["categories"][0]
            assert first.slug == "crypto"
            assert first.label == "Crypto"
            assert first.volume == 8000000.0
            assert first.market_count == 150


class TestCategoryMarketsFiltersCorrectly:
    """Tests for GET /api/v1/categories/{slug}/markets endpoint."""

    @pytest.fixture
    def client(self) -> "PolymarketClient":
        from app.services.polymarket import PolymarketClient
        return PolymarketClient()

    @pytest.fixture
    def mock_markets_response(self) -> list[dict]:
        """Mock markets API response."""
        return [
            {
                "id": "market-1",
                "question": "Will BTC reach 100k?",
                "volume": 5000000,
                "outcomePrices": {"Yes": "0.60", "No": "0.40"},
                "category": "crypto",
                "active": True,
                "closed": False,
            },
            {
                "id": "market-2",
                "question": "Will ETH hit 5k?",
                "volume": 3000000,
                "outcomePrices": {"Yes": "0.45", "No": "0.55"},
                "category": "crypto",
                "active": True,
                "closed": False,
            },
            {
                "id": "market-3",
                "question": "Will there be a Super Bowl?",
                "volume": 1000000,
                "outcomePrices": {"Yes": "0.99", "No": "0.01"},
                "category": "sports",
                "active": True,
                "closed": False,
            },
        ]

    @pytest.mark.asyncio
    async def test_category_markets_filters_by_slug(
        self,
        client: "PolymarketClient",
        mock_markets_response: list[dict],
    ) -> None:
        """Verify markets are filtered by category slug correctly."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_markets,
        ):
            mock_markets.return_value = mock_markets_response

            result = await categories_service.get_markets_by_category(
                client, slug="crypto", limit=20, offset=0
            )

            # Verify only crypto markets are returned
            assert "markets" in result
            assert len(result["markets"]) == 2
            for market in result["markets"]:
                assert market.category == "crypto"

    @pytest.mark.asyncio
    async def test_category_markets_returns_pagination(
        self,
        client: "PolymarketClient",
        mock_markets_response: list[dict],
    ) -> None:
        """Verify category markets returns pagination info."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_markets,
        ):
            mock_markets.return_value = mock_markets_response

            result = await categories_service.get_markets_by_category(
                client, slug="crypto", limit=10, offset=0
            )

            # Verify pagination fields
            assert "total" in result
            assert "has_more" in result
            assert result["total"] == 2
            assert result["has_more"] is False

    @pytest.mark.asyncio
    async def test_category_markets_with_pagination_offset(
        self,
        client: "PolymarketClient",
        mock_markets_response: list[dict],
    ) -> None:
        """Verify category markets pagination with offset works."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_markets,
        ):
            mock_markets.return_value = mock_markets_response

            result = await categories_service.get_markets_by_category(
                client, slug="crypto", limit=1, offset=0
            )

            # Verify pagination with offset
            assert len(result["markets"]) == 1
            assert result["total"] == 2
            assert result["has_more"] is True

    @pytest.mark.asyncio
    async def test_category_markets_empty_for_unknown_slug(
        self,
        client: "PolymarketClient",
        mock_markets_response: list[dict],
    ) -> None:
        """Verify empty list returned for unknown category slug."""
        with (
            patch.object(client, "get_trending_markets", new_callable=AsyncMock) as mock_markets,
        ):
            mock_markets.return_value = mock_markets_response

            result = await categories_service.get_markets_by_category(
                client, slug="unknown-category", limit=20, offset=0
            )

            # Verify no markets returned for unknown category
            assert len(result["markets"]) == 0
            assert result["total"] == 0
            assert result["has_more"] is False
