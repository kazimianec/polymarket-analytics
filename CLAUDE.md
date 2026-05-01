# Polymarket Analytics — Project Vision

## What This Project Does

Analyze Polymarket prediction market data to surface statistics, trends, and interesting insights about how crowds predict future events.

## Data Sources

- **Gamma API** — market discovery, search, browsing
- **CLOB API** — real-time prices, orderbook, price history
- **Data API** — trades, open interest

All read-only, no authentication required.

## Analytics Capabilities

### 1. Market Statistics
- Total volume by category, time period, market state
- Active vs closed market counts
- Liquidity metrics (spread, orderbook depth)
- Price movement tracking

### 2. Topic & Trend Analysis
- Trending topics by volume
- Category distribution (crypto, sports, politics, entertainment, etc.)
- "Hot" markets — high volume or dramatic price swings
- Keyword/description clustering

### 3. Prediction Accuracy (Wisdom of the Crowd)
- Track resolved markets — compare final price to actual outcome
- Overall accuracy score across all resolved markets
- Per-category accuracy breakdown
- Identify systematic biases (over/underestimation)

### 4. Market Quality Metrics
- Spread analysis — how efficient are markets?
- Volume vs liquidity correlation
- Time-to-resolution patterns

### 5. Interesting Patterns
- Cross-market correlations
- Sentiment from market questions
- "Consensus" markets — where is the crowd most confident?
- Unusual activity detection

## Stack

- **Backend:** Python 3.12, FastAPI, Pydantic v2, httpx, polars
- **Frontend:** TypeScript, React 18, Vite, MUI v6, TanStack Query v5
- **Database:** PostgreSQL (raw SQL, no ORM)

## Engineering Philosophy

Follow the template's conventions (see original CLAUDE.md). Key reminders:
- Thin routers, fat services — business logic in `services/`
- No overengineering — solve the problem in front of you
- Raw SQL, no ORM
- All functions require type hints and docstrings

## API Design

```
GET /api/v1/stats/overview          — aggregate market statistics
GET /api/v1/stats/categories        — volume/distribution by category
GET /api/v1/markets/trending        — top markets by volume
GET /api/v1/markets/resolved        — recently resolved markets
GET /api/v1/markets/{id}/history    — price history for a market
GET /api/v1/accuracy/summary        — prediction accuracy metrics
GET /api/v1/accuracy/by-category    — accuracy broken down by category
GET /api/v1/search                 — search markets by keyword
```

## Frontend Pages

- **Dashboard** — overview stats, trending markets, category distribution
- **Markets** — searchable/filterable market list
- **Market Detail** — price history chart, orderbook, trade data
- **Accuracy** — prediction accuracy analytics by category
- **Topics** — topic clustering and trend analysis
