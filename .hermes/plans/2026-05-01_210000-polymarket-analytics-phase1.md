# Polymarket Analytics — Phase 1 Implementation Plan

**Goal:** Build the data fetching layer + core dashboard UI

## Context

- Template project uses Python 3.12 + FastAPI (backend) and React 18 + Vite + MUI (frontend)
- Polymarket has 3 public read-only APIs: Gamma (discovery), CLOB (prices/history), Data API (trades)
- All data is public, no auth needed

## Approach

Two parallel workstreams:
- **Track A:** Backend (API client + endpoints)
- **Track B:** Frontend (API hooks + pages)

Each follows TDD principles. Track A is prerequisite for Track B's API integration.

---

## Track A: Backend

### Task A-1: Polymarket API Client Service

**Files to create/modify:**
- `backend/src/app/services/polymarket.py` — API client wrapping httpx calls to Gamma, CLOB, Data APIs
- `backend/tests/test_polymarket_service.py` — tests

**Requirements:**
- Functions: `search_markets()`, `get_markets()`, `get_market_history()`, `get_market_detail()`
- Parse double-encoded JSON fields (`outcomePrices`, `clobTokenIds`, etc.)
- Proper error handling for HTTP errors
- Type hints + docstrings on all functions

**Tests:**
- Test that `search_markets("bitcoin")` returns parsed events with markets
- Test that `get_market_history(condition_id)` returns price history
- Test double-encoded field parsing

---

### Task A-2: Stats Overview Endpoint

**Files to create/modify:**
- `backend/src/app/routers/domain/stats.py`
- `backend/src/app/services/stats.py`
- `backend/src/app/models/responses/stats.py`
- `backend/tests/test_stats.py`

**Requirements:**
- `GET /api/v1/stats/overview` — returns:
  - Total active markets count
  - Total volume (sum across active markets)
  - Category distribution (top 10 categories by volume)
  - Top 5 trending markets by volume

**Tests:**
- Test endpoint returns expected structure
- Test category distribution calculation

---

### Task A-3: Trending Markets Endpoint

**Files to create/modify:**
- `backend/src/app/routers/domain/markets.py`
- `backend/src/app/services/markets.py`
- `backend/src/app/models/responses/market.py`
- `backend/tests/test_markets.py`

**Requirements:**
- `GET /api/v1/markets/trending` — top N markets by volume, with pagination
- `GET /api/v1/markets/{market_id}` — single market detail (question, prices, volume, odds)
- `GET /api/v1/markets/{market_id}/history` — price history from CLOB API

**Tests:**
- Test trending returns list of markets with correct fields
- Test market detail returns full info
- Test history returns timestamped price array

---

### Task A-4: Category Stats Endpoint

**Files to create/modify:**
- `backend/src/app/routers/domain/categories.py`
- `backend/src/app/services/categories.py`
- `backend/tests/test_categories.py`

**Requirements:**
- `GET /api/v1/stats/categories` — volume + market count per category
- `GET /api/v1/categories/{slug}/markets` — markets in a specific category

**Tests:**
- Test category list returns slug/label/volume/count
- Test category markets filter correctly

---

## Track B: Frontend

### Task B-1: API Hooks

**Files to create/modify:**
- `frontend/src/api/polymarket.ts` — TanStack Query hooks

**Requirements:**
- `useStatsOverview()` — fetch dashboard stats
- `useTrendingMarkets(limit?)` — fetch trending markets
- `useMarketDetail(id)` — fetch single market
- `useMarketHistory(id)` — fetch price history
- `useCategories()` — fetch category stats

**Tests:** Not required for frontend hooks (manual testing via browser)

---

### Task B-2: Dashboard Page

**Files to create/modify:**
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/components/dashboard/StatsOverview.tsx`
- `frontend/src/components/dashboard/TrendingMarkets.tsx`
- `frontend/src/components/dashboard/CategoryDistribution.tsx`

**Requirements:**
- Stats cards: total markets, total volume, top category
- Trending markets list (question, odds as %, volume)
- Category distribution chart (bar or pie chart using MUI)
- Loading + error states

**Tech:** MUI components, Recharts for charts

---

### Task B-3: Market Detail Page

**Files to create/modify:**
- `frontend/src/pages/MarketDetailPage.tsx`
- `frontend/src/components/market/PriceChart.tsx`
- `frontend/src/components/market/MarketInfo.tsx`

**Requirements:**
- Market question as title
- Current odds displayed as large % (Yes/No)
- Price history line chart (Recharts)
- Volume displayed
- Link back to dashboard

**Tests:** Playwright screenshot test

---

## Verification

1. Run backend: `make dev-backend` — verify endpoints respond
2. Run frontend: `make dev-frontend` — verify page loads
3. `make test-backend` — all tests pass
4. Playwright: screenshot dashboard page

## Risks

- Polymarket API rate limits (unlikely for normal use)
- New markets may have empty price history
- Category/tag slugs may be inconsistent

## Open Questions

- Do we store data in PostgreSQL for historical analysis, or just proxy live data? → **Phase 1: proxy only, no DB**
- Which chart library? → **Recharts** (lightweight, works well with React)
