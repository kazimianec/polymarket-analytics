"""Stats aggregation service.

Business logic for computing aggregate market statistics from Polymarket data.
"""

import logging
from typing import TypedDict

from app.models.responses.stats import (
    CategoryItem,
    StatsOverviewResponse,
    TrendingMarketItem,
)
from app.services.polymarket import PolymarketClient

logger = logging.getLogger(__name__)

GAMMA_BASE = "https://gamma-api.polymarket.com"


class StatsOverviewDict(TypedDict):
    """Dictionary structure returned by get_stats_overview."""

    total_active_markets: int
    total_volume: float
    top_categories: list[CategoryItem]
    trending_markets: list[TrendingMarketItem]


async def get_stats_overview(client: PolymarketClient) -> StatsOverviewDict:
    """Get aggregate market statistics overview.

    Fetches trending markets and category/tag data from Polymarket APIs
    and computes aggregate statistics.

    Args:
        client: PolymarketClient instance for making API calls.

    Returns:
        StatsOverviewDict with total_active_markets, total_volume,
        top_categories, and trending_markets.
    """
    # Get trending markets (active, not closed)
    trending_markets = await client.get_trending_markets(limit=20)

    # Calculate total volume and build trending market items
    total_volume = 0.0
    trending_items: list[TrendingMarketItem] = []

    for market in trending_markets:
        volume = float(market.get("volume", 0) or 0)
        total_volume += volume

        # Extract yes/no prices from outcomePrices
        outcome_prices = market.get("outcomePrices", {})
        if isinstance(outcome_prices, str):
            # Handle double-encoded JSON string
            import json

            try:
                outcome_prices = json.loads(outcome_prices)
            except (json.JSONDecodeError, TypeError):
                outcome_prices = {}

        yes_price = float(outcome_prices.get("Yes", 0.5) or 0.5)
        no_price = float(outcome_prices.get("No", 0.5) or 0.5)

        trending_items.append(
            TrendingMarketItem(
                id=market.get("id", ""),
                question=market.get("question", ""),
                yes_price=yes_price,
                no_price=no_price,
                volume=volume,
            )
        )

    # Get tags for category distribution
    tags_response = await client._get(GAMMA_BASE, "/tags")
    tags = tags_response.get("tags", [])

    # Build top categories sorted by volume
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

    # Sort by volume descending and take top 10
    categories.sort(key=lambda c: c.volume, reverse=True)
    top_categories = categories[:10]

    return StatsOverviewDict(
        total_active_markets=len(trending_markets),
        total_volume=total_volume,
        top_categories=top_categories,
        trending_markets=trending_items,
    )
