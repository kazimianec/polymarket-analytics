"""Categories domain service.

Business logic for fetching and aggregating category data from Polymarket APIs.
"""

import logging
from typing import TypedDict

from app.models.responses.category import CategoryItem, CategoryListResponse
from app.models.responses.market import TrendingMarketItem, TrendingMarketsResponse
from app.services.polymarket import PolymarketClient

logger = logging.getLogger(__name__)

GAMMA_BASE = "https://gamma-api.polymarket.com"


class CategoryListDict(TypedDict):
    """Dictionary structure returned by get_categories."""

    categories: list[CategoryItem]


class CategoryMarketsDict(TypedDict):
    """Dictionary structure returned by get_markets_by_category."""

    markets: list[TrendingMarketItem]
    total: int
    has_more: bool


async def get_categories(client: PolymarketClient) -> CategoryListDict:
    """Get all categories with volume and market count from Polymarket.

    Fetches category/tag data from Polymarket Gamma API and returns
    aggregated category statistics.

    Args:
        client: PolymarketClient instance for making API calls.

    Returns:
        CategoryListDict with list of categories sorted by volume.
    """
    # Get tags for category distribution
    tags_response = await client._get(GAMMA_BASE, "/tags")
    tags = tags_response.get("tags", [])

    # Build categories sorted by volume
    categories: list[CategoryItem] = []
    for tag in tags:
        if isinstance(tag, dict):
            categories.append(
                CategoryItem(
                    slug=tag.get("slug", ""),
                    label=tag.get("label", tag.get("slug", "")),
                    volume=float(tag.get("volume", 0) or 0),
                    market_count=int(tag.get("marketCount", tag.get("market_count", 0)) or 0),
                )
            )

    # Sort by volume descending
    categories.sort(key=lambda c: c.volume, reverse=True)

    return CategoryListDict(categories=categories)


async def get_markets_by_category(
    client: PolymarketClient, slug: str, limit: int = 20, offset: int = 0
) -> CategoryMarketsDict:
    """Get markets filtered by category slug with pagination.

    Fetches all markets from Polymarket Gamma API and filters by category.

    Args:
        client: PolymarketClient instance for making API calls.
        slug: Category slug to filter markets by.
        limit: Maximum number of markets to return.
        offset: Number of markets to skip for pagination.

    Returns:
        CategoryMarketsDict with markets list, total count, and has_more flag.
    """
    # Get all trending markets (we need to filter client-side by category)
    all_markets = await client.get_trending_markets(limit=100)

    # Filter by category slug
    filtered_markets = [
        market for market in all_markets
        if market.get("category") == slug
    ]

    # Apply pagination
    total = len(filtered_markets)
    paginated_markets = filtered_markets[offset : offset + limit]

    # Transform to response models
    market_items: list[TrendingMarketItem] = []
    for market in paginated_markets:
        # Extract yes/no prices from outcomePrices
        outcome_prices = market.get("outcomePrices", {})
        if isinstance(outcome_prices, str):
            import json

            try:
                outcome_prices = json.loads(outcome_prices)
            except (json.JSONDecodeError, TypeError):
                outcome_prices = {}

        yes_price = float(outcome_prices.get("Yes", 0.5) if outcome_prices else 0.5)
        no_price = float(outcome_prices.get("No", 0.5) if outcome_prices else 0.5)

        # Get category
        category = market.get("category") or None

        # Get end date
        end_date = market.get("endDate") or market.get("end_date") or None

        market_items.append(
            TrendingMarketItem(
                id=market.get("id", ""),
                question=market.get("question", ""),
                yes_price=yes_price,
                no_price=no_price,
                volume=float(market.get("volume", 0) or 0),
                liquidity=float(market.get("liquidity", 0) or 0),
                category=category,
                end_date=end_date,
                active=bool(market.get("active", True)),
                closed=bool(market.get("closed", False)),
            )
        )

    has_more = offset + limit < total

    return CategoryMarketsDict(
        markets=market_items,
        total=total,
        has_more=has_more,
    )
