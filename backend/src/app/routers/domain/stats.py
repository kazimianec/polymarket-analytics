"""Stats domain router.

Thin FastAPI router for stats endpoints - delegates all logic to services.
"""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.models.responses.stats import StatsOverviewResponse
from app.services.polymarket import PolymarketClient
from app.services import stats as stats_service

router = APIRouter(tags=["stats"])


async def get_polymarket_client() -> PolymarketClient:
    """Dependency that provides a PolymarketClient instance."""
    return PolymarketClient()


@router.get("/stats/overview", response_model=StatsOverviewResponse)
async def get_stats_overview(
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
) -> StatsOverviewResponse:
    """Return aggregate market statistics overview.

    Provides:
    - Total count of active markets
    - Total trading volume
    - Top categories by volume
    - Trending markets with prices and volumes

    Returns:
        StatsOverviewResponse with aggregated market statistics.
    """
    result = await stats_service.get_stats_overview(client)
    return StatsOverviewResponse(**result)
