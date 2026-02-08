# Frontend Integration Guide: Live Market Data Updates

This document summarizes the recent infrastructure changes to the `/api/live` routes. Most changes are internal (backwards compatible), but there are new features and security constraints you should implement.

## 1. What's NEW (Capabilities)

### Pagination Support
Routes for listing stocks and crypto now support direct pagination. 
- **Affected Routes**: `/api/live/stocks`, `/api/live/crypto`
- **Parameters**: `page` (default: 1), `limit` (default: 25/50, max: 100)
- **Usage**: You can now implement "Load More" or "Infinite Scroll" by incrementing the page number.

### Standardized Data Format
All items returned from the live routes now go through a unified formatter.
- **Fields preserved**: `symbol`, `name`, `price`, `change`, `changePercent`, `volume`, `marketCap`, `assetType`, `currency`, `exchange`.
- **New Field**: `lastUpdated` (ISO timestamp). Use this to show a "last updated at..." message to the user.
- **Data Integrity**: All numeric fields (price, change, etc.) are now strictly returned as `floats`. You no longer need to manually parse strings.

## 2. What's REMAINED (No Action Required)

- **Variable Names**: The keys in the JSON objects have NOT changed. Your existing variable mappings will continue to work.
- **Endpoint URLs**: All existing paths remain the same.
- **Chart Data**: The `/api/live/intraday/<symbol>` structure remains identical to minimize friction with your chart library.

## 3. Security & PERFORMANCE (Action Required)

### Rate Limiting (Professional Standards)
We have implemented a professional security gatekeeper. If the site refresh rate is too high, the server will return a `429 Too Many Requests` error.
- **Action**: Ensure your auto-refresh/polling logic is NOT faster than every **5-10 seconds**.
- **UX Recommendation**: If you receive a `429` error, show a toast notification: *"You are refreshing too fast. Please wait a moment."*

### Caching
The server now saves prices for **15-30 seconds**. 
- **Effect**: If the user refreshes manually within this window, they will get the cached data instantly. The data is still "live," but optimized for server stability.

---

## Example Usage (New Pagination)

```javascript
/* Implementing Infinite Scroll */
const fetchNextPage = async (pageNumber) => {
  const response = await fetch(`/api/live/stocks?page=${pageNumber}&limit=50`);
  const data = await response.json();
  // Standard float fields are ready to use
  console.log(data[0].price); // Guaranteed to be a number, not a string
};
```

## Support for 429 Errors
```javascript
if (response.status === 429) {
  showNotification("Rate limit exceeded. Slow down!");
}
```
