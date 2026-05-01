"""Response models for stats endpoints."""

from pydantic import BaseModel


class TrendingMarketItem(BaseModel):
    """A single trending market in the stats overview."""

    id: str
    question: str
    yes_price: float
    no_price: float
    volume: float


class CategoryItem(BaseModel):
    """A single category in the stats overview."""

    slug: str
    label: str
    volume: float
    market_count: int


class StatsOverviewResponse(BaseModel):
    """Response model for GET /api/v1/stats/overview."""

    total_active_markets: int
    total_volume: float
    top_categories: list[CategoryItem]
    trending_markets: list[TrendingMarketItem]
