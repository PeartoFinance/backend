# Chart & Asset API Documentation (Frontend Integration)

This document outlines the recent backend changes to timeframes, caching, and asset detection. Frontend developers should follow these rules to ensure smooth chart rendering and prevent 404 errors.

---

## 1. Chart Timeframe Limitations (The "1-Minute" Rule)
The backend now includes **Smart Validation** to prevent 404 crashes from Yahoo Finance.

| Interval (interval) | Valid Periods (period) | Backend Behavior if Invalid |
| :--- | :--- | :--- |
| **1m** | 1d, 5d, 7d | **Defaults to 1d** |
| **2m - 90m** | 1d up to 1mo | **Capped at 1mo** |
| **1d (Daily)** | 1mo to Max | Works as intended |

**Frontend Tip**: If a user selects "1 minute" interval, it is best to set the UI period to "1 Day" by default. Requesting "1 Year" of "1 Minute" data will now be automatically downgraded to "1 Day" by the backend to prevent a crash.

---

## 2. Updated Asset Types
The backend now automatically detects the asset type during search and discovery. Ensure your UI handles these labels for icons and formatting:

- `stock`: Standard Equities/Stocks.
- `crypto`: Cryptocurrencies (Symbols ending in `-USD`).
- `commodity`: Gold, Silver, Oil (Symbols ending in `=F`).
- `index`: Market Indices (S&P 500, etc.) and Forex pairs.
- `etf`: Exchange Traded Funds.

---

## 3. Handling API Caching & Performance
We have implemented a **Dual-Layer Cache** to protect against Yahoo rate limits:

1.  **Memory Cache (5 Min)**: The backend remembers chart data for 5 minutes. If the user refreshes quickly, the data is served instantly without hitting Yahoo.
2.  **Discovery Lock (10 Sec)**: When searching for a brand-new symbol, the first request "locks" the import process. 
    - **Frontend Tip**: If the frontend makes 5 parallel requests for a new stock, the backend will make them wait ~500ms so they don't all trigger Yahoo at once. **Do not timeout requests under 2 seconds during discovery search.**

---

## 4. Error Handling
If you receive a **404 error**, it strictly means:
- The symbol does not exist on Yahoo Finance.
- The symbol is not supported for that specific country filter.

If the chart loads but you see a **"Stock Not Found"** banner, check if your different API calls (Profile vs. History) are using consistent symbols (e.g., ensure both are Uppercase).

---

**Last Updated**: 2026-02-24  
**Status**: Deployed & Consistent across Stocks, Crypto, and Forex routes.
