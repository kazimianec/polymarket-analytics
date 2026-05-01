# Polymarket API Notes

## Overview

Polymarket provides three public APIs for reading market data. All endpoints are read-only and do not require authentication.

## API Endpoints

### Gamma API — `https://gamma-api.polymarket.com`

Market discovery, search, and browsing.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/events` | GET | List events with nested markets |
| `/markets` | GET | List markets |
| `/public-search` | GET | Search markets by keyword |
| `/tags` | GET | List all tags |

**Common query parameters:**
- `limit` — number of results
- `active=true` — only active markets
- `closed=false` — exclude closed markets
- `order=volume` — sort by volume
- `ascending=false` — descending order

**Important:** Gamma API returns `outcomePrices`, `outcomes`, `clobTokenIds` as JSON **strings** (double-encoded). Must parse with `json.loads()`.

Example response field:
```json
{
  "outcomes": "[\"Yes\", \"No\"]",
  "outcomePrices": "{\"Yes\": \"0.45\", \"No\": \"0.55\"}",
  "clobTokenIds": "[\"token-abc\", \"token-def\"]"
}
```

### CLOB API — `https://clob.polymarket.com`

Real-time prices and orderbook data.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/price` | GET | Current price for a token |
| `/midpoint` | GET | Midpoint price |
| `/prices-history` | GET | Price history |

**Query parameters:**
- `token_id` — token identifier (for price/midpoint)
- `market` — condition ID (for price history)
- `interval` — time interval (e.g., "1d", "1h")
- `fidelity` — resolution (higher = more data points)

**Price history response format:**
```json
[
  {"t": 1704067200, "p": 0.45},
  {"t": 1704153600, "p": 0.48}
]
```
Where `t` is Unix timestamp and `p` is price.

### Data API — `https://data-api.polymarket.com`

Trade data and volume.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/trades` | GET | Recent trades |

**Query parameters:**
- `market` — condition ID
- `limit` — max trades to return

## Data Types

### Condition ID vs Market ID

- **Condition ID** — used for CLOB and Data APIs (price history, trades)
- **Market ID** — used for Gamma API (market details)

These are different identifiers for the same underlying market.

## Rate Limits

- Gamma API: ~120 requests/minute
- CLOB API: ~60 requests/minute
- Data API: ~60 requests/minute

## Error Handling

All APIs return standard HTTP status codes. Custom `PolymarketHTTPError` exception is raised for 4xx/5xx responses.

## References

- [Polymarket API Docs](https://docs.polymarket.com)
- [Gamma API Specification](https://gamma-api.polymarket.com)
