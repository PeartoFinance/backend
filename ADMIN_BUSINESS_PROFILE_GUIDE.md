# Admin Guide: Business Profile Management

This guide explains how to use the new Admin APIs to manage the *Business Profile* feature. These routes allow you to approve companies for the public directory, sync their financial data from Yahoo Finance, and manage market alerts.

---

## 1. Sync Financial Data (Automated)
This route automatically pulls historical financial statements from Yahoo Finance and stores them in our database.

*   **Endpoint**: `POST /api/admin/market/business/sync-financials`
*   **Purpose**: To populate the "Financials" tab (Revenue, Net Income, Assets, etc.) for a specific company.
*   **Request Body**:
    ```json
    {
        "symbol": "AAPL",
        "period": "annual" 
    }
    ```
    *(Note: `period` can be "annual" or "quarterly")*
*   **What it does**: 
    1.  Connects to Yahoo Finance API.
    2.  Downloads the Income Statement, Balance Sheet, and Cash Flow.
    3.  Stores Revenue, Net Income, Total Assets, Total Liabilities, and Cash Flow in the `company_financials` table.
    4.  Updates existing records if the date matches, so data is never duplicated.
    
---

## 2. Sync Forecast Data (Automated)
This pulls the analyst price targets and "Buy/Sell" consensus shown in the Tesla example.

*   **Endpoint**: `POST /api/admin/market/business/sync-forecast`
*   **Purpose**: To populate the "Forecast" tab (Price Targets, Analyst Ratings).
*   **Request Body**:
    ```json
    {
        "symbol": "TSLA"
    }
    ```
*   **What it does**: 
    1.  Fetches High, Low, and Mean price targets.
    2.  Fetches Analyst Consensus (Strong Buy, Buy, Hold, etc.).
    3.  Stores data in the `analyst_recommendations` table.

---

## 3. Toggle Public Listing (Manual Approval)
By default, new stocks are **hidden** from the public Business Directory. Use this route to "Approve" or "Feature" a company.

*   **Endpoint**: `POST /api/admin/market/business/toggle-listing`
*   **Purpose**: To decide which companies appear in the public list (`/api/stocks/directory`).
*   **Request Body**:
    ```json
    {
        "symbol": "AAPL",
        "is_listed": true
    }
    ```
*   **What it does**: 
    - Sets the `is_listed` flag in the `market_data` table.
    - If `true`, the company appears in the public directory and its full profile becomes accessible.

---

## 3. Add Market Issue / Alert (Manual)
Sometimes a company has risks or news that isn't in the automated data (e.g., a lawsuit or a regulatory warning). Admins can add these manually.

*   **Endpoint**: `POST /api/admin/market/business/add-issue`
*   **Purpose**: To show a "Warning" or "Notice" banner on the company's profile.
*   **Request Body**:
    ```json
    {
        "symbol": "AAPL",
        "title": "Regulatory Investigation",
        "description": "The company is currently under review for antitrust concerns in Europe.",
        "severity": "warning"
    }
    ```
    *(Severity levels: `info`, `warning`, `critical`)*
*   **What it does**: Stores a record in the `market_issues` table linked to that symbol.

---

## 4. View & Manage Issues
Use these routes to see what alerts are currently active and remove them once the issue is resolved.

### Get All Issues for a Company
*   **Endpoint**: `GET /api/admin/market/business/issues/<symbol>`
*   **Returns**: A list of all historical and active issues for that company.

### Resolve/Delete an Issue
*   **Endpoint**: `DELETE /api/admin/market/business/issues/<issue_id>`
*   **Purpose**: To remove an alert from the public profile once the situation is resolved.
*   **What it does**: Marks the issue as `is_active = False` in the database.

---

## Summary of Data Sources

| Feature | Source | Admin Action |
| :--- | :--- | :--- |
| **Stock Price / Stats** | Yahoo Finance (Auto) | No action needed. |
| **Financials (Revenue/Income)** | Yahoo Finance (Auto) | **Must trigger** the "Sync Financials" route once. |
| **Company Description/Logo** | Yahoo Finance (Auto) | No action needed (fetched during initial import). |
| **Public Visibility** | Manual | **Must toggle** `is_listed` to `true`. |
| **Market Issues/Alerts** | Manual | **Must add** manually via the "Add Issue" route. |
| **Related News** | Mixed | Auto-linked if the symbol is mentioned; can be manually linked in DB. |

---

## Authentication Note
All these routes require a **Bearer Token** in the header.
`Authorization: Bearer <your_admin_jwt_token>`
