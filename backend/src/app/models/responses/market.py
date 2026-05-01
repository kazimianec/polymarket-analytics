"""Response models for markets endpoints."""

from pydantic import BaseModel


class TrendingMarketItem(BaseModel):
    """A single market in the trending markets list."""

    id: str
    question: str
    yes_price: float
    no_price: float
    volume: float
    liquidity: float
    category: str | None
    end_date: str | None
    active: bool
    closed: bool


class TrendingMarketsResponse(BaseModel):
    """Response model for GET /api/v1/markets/trending."""

    markets: list[TrendingMarketItem]
    total: int
    has_more: bool


class MarketDetailResponse(BaseModel):
    """Response model for GET /api/v1/markets/{market_id}."""

    id: str
    question: str
    description: str
    yes_price: float
    no_price: float
    volume: float
    liquidity: float
    category: str | None
    end_date: str | None
    outcomes: list[str]
    active: bool
    closed: bool
    condition_id: str
    clob_token_ids: list[str]


class PricePoint(BaseModel):
    """A single price point in market history."""

    timestamp: int
    price: float


class MarketHistoryResponse(BaseModel):
    """Response model for GET /api/v1/markets/{market_id}/history."""

    history: list[PricePoint]
