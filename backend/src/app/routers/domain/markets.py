"""Markets domain router.

Thin FastAPI router for markets endpoints - delegates all logic to services.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.models.responses.market import (
    MarketDetailResponse,
    MarketHistoryResponse,
    TrendingMarketsResponse,
)
from app.services.polymarket import PolymarketClient
from app.services import markets as markets_service

router = APIRouter(tags=["markets"])


async def get_polymarket_client() -> PolymarketClient:
    """Dependency that provides a PolymarketClient instance."""
    return PolymarketClient()


@router.get("/markets/trending", response_model=TrendingMarketsResponse)
async def get_trending_markets(
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
    limit: int = 20,
    offset: int = 0,
) -> TrendingMarketsResponse:
    """Return top markets by volume with pagination.

    Provides:
    - List of active markets sorted by trading volume descending
    - Pagination support with limit and offset
    - Total count and has_more flag for pagination

    Args:
        limit: Maximum number of markets to return (default 20, max 100).
        offset: Number of markets to skip for pagination.

    Returns:
        TrendingMarketsResponse with paginated markets list.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be non-negative")

    result = await markets_service.get_trending_markets(client, limit=limit, offset=offset)
    return TrendingMarketsResponse(**result)


@router.get("/markets/{market_id}", response_model=MarketDetailResponse)
async def get_market_detail(
    market_id: str,
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
) -> MarketDetailResponse:
    """Return detailed information for a single market.

    Provides:
    - Full market details including question, description
    - Current yes/no prices
    - Volume and liquidity metrics
    - Outcomes, category, and end date
    - Condition ID and CLOB token IDs for API integration

    Args:
        market_id: Unique market identifier.

    Returns:
        MarketDetailResponse with full market information.

    Raises:
        HTTPException: 404 if market not found.
    """
    result = await markets_service.get_market_detail(client, market_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Market not found")
    return result


@router.get("/markets/{market_id}/history", response_model=MarketHistoryResponse)
async def get_market_history(
    market_id: str,
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
    interval: str = "1d",
    fidelity: int = 50,
) -> MarketHistoryResponse:
    """Return price history for a market.

    Provides:
    - Historical price data points with timestamps
    - Configurable interval and fidelity

    Args:
        market_id: Market condition ID.
        interval: Time interval for price points (e.g., "1d", "1h").
        fidelity: Resolution/fidelity of the price data (higher = more data).

    Returns:
        MarketHistoryResponse with list of price points.
    """
    result = await markets_service.get_market_history(
        client, market_id, interval=interval, fidelity=fidelity
    )
    return result
