# Business Profile Feature - Implementation Summary

This document summarizes the backend work completed to support the new **Business Profile** feature (Apple/Tesla/Amazon style).

---

## 2. Admin Backend (The "Control Room")
Admins now have full control over the data.
*   **Automated Sync**: New routes to pull **Financials** and **Analyst Forecasts** (Price Targets) directly from Yahoo Finance into our DB.
*   **Manual Approval**: Admins must toggle `is_listed = True` for a stock to appear in the public directory.
*   **Manual Alerts**: Admins can add/remove "Market Issues" (e.g., "Regulatory Warning") that appear as banners on the profile.

---

## 3. Public API (Guide for Frontend Developers)
The Public API has been refactored into a **Tab-Based Structure**. Instead of loading everything at once, you can load data for each tab as the user clicks it.

### **Main Profile (Overview Tab)**
*   **Route**: `GET /api/stocks/profile/<symbol>`
*   **Usage**: Use this for the header (Price, Change) and the "Overview" tab.
*   **Key Fields**: `description`, `sector`, `industry`, `marketIssues` (alerts), and `news`.

### **Financials Tab**
*   **Route**: `GET /api/stocks/financials/<symbol>`
*   **Usage**: Returns a list of historical financial records.
*   **Data**: `revenue`, `net_income`, `total_assets`, `free_cash_flow`, etc.

### **Forecast Tab**
*   **Route**: `GET /api/stocks/forecast/<symbol>`
*   **Usage**: Use this for the "Price Target" chart and the "Analyst Consensus" gauge.
*   **Data**: `target_high`, `target_low`, `target_mean`, and counts for `buy`/`sell`/`hold`.

### **Statistics Tab**
*   **Route**: `GET /api/stocks/statistics/<symbol>`
*   **Usage**: Returns technical data points.
*   **Data**: `peRatio`, `eps`, `beta`, `sharesOutstanding`, `52WeekRange`.

### **Dividends Tab**
*   **Route**: `GET /api/stocks/dividends/<symbol>`
*   **Usage**: Returns the history of dividend payments.

---

## 4. Important Logic Changes
*   **Curated Directory**: All search and listing routes (Movers, Most Active, Search) now only return stocks where `is_listed = True`.
*   **Performance**: Financial and Forecast data is served from our database (fast) rather than calling Yahoo Finance directly (slow).

---

## How to Implement in Frontend:
1.  **Update Search**: The search results will now only show "Approved" businesses.
2.  **Tab Loading**: When a user clicks a tab (e.g., "Financials"), make a call to the specific route for that tab.
3.  **Alert Banners**: Always check the `marketIssues` array in the main profile response. If it contains active issues, show a warning banner at the top of the page.
