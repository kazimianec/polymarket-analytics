"""Response models for category endpoints."""

from pydantic import BaseModel


class CategoryItem(BaseModel):
    """A single category with volume and market count."""

    slug: str
    label: str
    volume: float
    market_count: int


class CategoryListResponse(BaseModel):
    """Response model for GET /api/v1/stats/categories."""

    categories: list[CategoryItem]
