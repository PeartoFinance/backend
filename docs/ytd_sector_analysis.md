# YTD & Sector Analysis API Documentation

This document explains the new Year-to-Date (YTD) return features and the updated Sector Analysis API.

## 1. Sector Analysis Endpoint

**URL:** `GET /api/market/sector-analysis`  
**Authentication:** Optional (Public)  
**Headers (Optional):** `X-User-Country` (Filters data by country, defaults to 'GLOBAL')

### Response Structure
The endpoint returns a breakdown of market sectors updated with performance metrics.

```json
{
  "sectors": [
    {
      "sector": "Technology",
      "stockCount": 42,
      "weight": 15.5,
      "avgYtdReturn": 12.35,
      "avgChangePercent": 1.2,
      "turnover": 5000234.5,
      "turnoverPercent": 20.1,
      "volume": 1200000,
      "volumePercent": 18.5,
      "advancers": 30,
      "decliners": 10,
      "unchanged": 2
    },
    ...
  ],
  "totals": {
    "turnover": 25000000.0,
    "volume": 6500000,
    "stockCount": 271,
    "sectorCount": 11
  }
}
```

### Key Field Definitions:
*   `stockCount`: Total number of listed stocks in this sector.
*   `weight`: Percentage of the total market represented by this sector (calculated by stock count).
*   `avgYtdReturn`: The **Average Year-to-Date performance** of all stocks in this sector. Use this for YTD charts.
*   `avgChangePercent`: The **Average Daily performance** (today's change).

## 2. Individual Stock Data (YTD)

The `MarketData` model now includes a `ytdReturn` field. This is available in all stock listing endpoints (e.g., `/api/market/stocks`, `/api/live/quote/<symbol>`).

*   **Field Name:** `ytdReturn`
*   **Type:** `float` (Percentage, e.g., `15.5` for 15.5%)
*   **Availability:** Returns `null` if the data hasn't been calculated yet for that ticker.

## 3. Background Data Sync

*   **Logic:** The backend calculates YTD returns by fetching the price from Jan 1st of the current year and comparing it to the latest market price.
*   **Frequency:** Data is updated automatically **once a day at 1:00 AM**.
*   **Force Refresh:** If you need to trigger an update manually for testing, use the admin/cron route:
    `POST /api/cron/update-ytd?token=YOUR_TOKEN`

## 4. Implementation Notes for Frontend
*   **Visualization:** Use the `weight` field for Pie charts to show sector distribution.
*   **Performance:** Use `avgYtdReturn` for Bar charts to compare which sectors are winning/losing this year.
*   **Sorting:** The API returns sectors sorted by `turnover` (highest volume * price) by default.
