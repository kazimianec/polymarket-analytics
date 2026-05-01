"""Categories domain router.

Thin FastAPI router for category endpoints - delegates all logic to services.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.models.responses.category import CategoryListResponse
from app.models.responses.market import TrendingMarketsResponse
from app.services.polymarket import PolymarketClient
from app.services import categories as categories_service

router = APIRouter(tags=["categories"])


async def get_polymarket_client() -> PolymarketClient:
    """Dependency that provides a PolymarketClient instance."""
    return PolymarketClient()


@router.get("/stats/categories", response_model=CategoryListResponse)
async def get_categories(
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
) -> CategoryListResponse:
    """Return all categories with volume and market count.

    Provides:
    - List of all categories from Polymarket
    - Volume and market count per category
    - Sorted by volume descending

    Returns:
        CategoryListResponse with list of categories.
    """
    result = await categories_service.get_categories(client)
    return CategoryListResponse(**result)


@router.get("/categories/{slug}/markets", response_model=TrendingMarketsResponse)
async def get_category_markets(
    slug: str,
    client: Annotated[PolymarketClient, Depends(get_polymarket_client)],
    limit: int = 20,
    offset: int = 0,
) -> TrendingMarketsResponse:
    """Return markets for a specific category with pagination.

    Provides:
    - List of markets in a specific category
    - Pagination support with limit and offset
    - Total count and has_more flag for pagination

    Args:
        slug: Category slug to filter markets by.
        limit: Maximum number of markets to return (default 20, max 100).
        offset: Number of markets to skip for pagination.

    Returns:
        TrendingMarketsResponse with paginated markets list.

    Raises:
        HTTPException: 400 if limit or offset is invalid.
    """
    if limit < 1 or limit > 100:
        raise HTTPException(status_code=400, detail="limit must be between 1 and 100")
    if offset < 0:
        raise HTTPException(status_code=400, detail="offset must be non-negative")

    result = await categories_service.get_markets_by_category(
        client, slug=slug, limit=limit, offset=offset
    )
    return TrendingMarketsResponse(**result)
