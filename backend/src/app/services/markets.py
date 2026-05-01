"""Markets domain service.

Business logic for fetching and transforming market data from Polymarket APIs.
"""

import logging
from typing import TypedDict

from app.models.responses.market import (
    MarketDetailResponse,
    MarketHistoryResponse,
    PricePoint,
    TrendingMarketItem,
    TrendingMarketsResponse,
)
from app.services.polymarket import PolymarketClient

logger = logging.getLogger(__name__)


class TrendingMarketsDict(TypedDict):
    """Dictionary structure returned by get_trending_markets."""

    markets: list[TrendingMarketItem]
    total: int
    has_more: bool


async def get_trending_markets(
    client: PolymarketClient, limit: int = 20, offset: int = 0
) -> TrendingMarketsDict:
    """Get paginated trending markets sorted by volume.

    Fetches active markets from Polymarket Gamma API, sorted by volume
    descending, and returns a paginated slice.

    Args:
        client: PolymarketClient instance for making API calls.
        limit: Maximum number of markets to return.
        offset: Number of markets to skip for pagination.

    Returns:
        TrendingMarketsDict with markets list, total count, and has_more flag.
    """
    # Get all trending markets (Gamma returns up to limit)
    all_markets = await client.get_trending_markets(limit=limit)

    # Apply pagination
    total = len(all_markets)
    paginated_markets = all_markets[offset : offset + limit]

    # Transform to response models
    market_items: list[TrendingMarketItem] = []
    for market in paginated_markets:
        # Extract yes/no prices from outcomePrices
        outcome_prices = market.get("outcomePrices", {})
        if isinstance(outcome_prices, str):
            # Handle double-encoded JSON string
            import json

            try:
                outcome_prices = json.loads(outcome_prices)
            except (json.JSONDecodeError, TypeError):
                outcome_prices = {}

        yes_price = float(outcome_prices.get("Yes", 0.5) if outcome_prices else 0.5)
        no_price = float(outcome_prices.get("No", 0.5) if outcome_prices else 0.5)

        # Get category from tags if available
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

    return TrendingMarketsDict(
        markets=market_items,
        total=total,
        has_more=has_more,
    )


async def get_market_detail(client: PolymarketClient, market_id: str) -> MarketDetailResponse | None:
    """Get detailed information for a single market.

    Fetches market details from Polymarket Gamma API by market ID.

    Args:
        client: PolymarketClient instance for making API calls.
        market_id: Unique market identifier.

    Returns:
        MarketDetailResponse with full market information, or None if not found.
    """
    market = await client.get_market_detail(market_id)
    if not market:
        return None

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

    # Get outcomes
    outcomes = market.get("outcomes", ["Yes", "No"])
    if isinstance(outcomes, str):
        import json

        try:
            outcomes = json.loads(outcomes)
        except (json.JSONDecodeError, TypeError):
            outcomes = ["Yes", "No"]

    # Get CLOB token IDs
    clob_token_ids = market.get("clobTokenIds", [])
    if isinstance(clob_token_ids, str):
        import json

        try:
            clob_token_ids = json.loads(clob_token_ids)
        except (json.JSONDecodeError, TypeError):
            clob_token_ids = []

    # Get category
    category = market.get("category") or None

    # Get end date
    end_date = market.get("endDate") or market.get("end_date") or None

    # Get condition_id (may be nested in market data)
    condition_id = market.get("conditionId", market.get("condition_id", ""))

    return MarketDetailResponse(
        id=market.get("id", ""),
        question=market.get("question", ""),
        description=market.get("description", ""),
        yes_price=yes_price,
        no_price=no_price,
        volume=float(market.get("volume", 0) or 0),
        liquidity=float(market.get("liquidity", 0) or 0),
        category=category,
        end_date=end_date,
        outcomes=outcomes,
        active=bool(market.get("active", True)),
        closed=bool(market.get("closed", False)),
        condition_id=condition_id,
        clob_token_ids=clob_token_ids,
    )


async def get_market_history(
    client: PolymarketClient, market_id: str, interval: str = "1d", fidelity: int = 50
) -> MarketHistoryResponse:
    """Get price history for a market.

    Fetches historical price data from Polymarket CLOB API.

    Args:
        client: PolymarketClient instance for making API calls.
        market_id: Market condition ID.
        interval: Time interval for price points (e.g., "1d", "1h").
        fidelity: Resolution/fidelity of the price data (higher = more data).

    Returns:
        MarketHistoryResponse with list of price points.
    """
    history_data = await client.get_market_history(market_id, interval=interval, fidelity=fidelity)

    price_points: list[PricePoint] = []
    for point in history_data:
        price_points.append(
            PricePoint(
                timestamp=int(point.get("t", 0)),
                price=float(point.get("p", 0.0)),
            )
        )

    return MarketHistoryResponse(history=price_points)
