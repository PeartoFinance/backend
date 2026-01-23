# Business Profile Feature Specification

## 1. Overview
The Business Profile feature aims to provide a comprehensive view of a listed company, similar to professional platforms like Yahoo Finance or Seeking Alpha. It allows users to explore a company's financial health, historical performance, news, and potential market risks.

The profile will be organized into several tabs:
- **Overview**: Real-time price, key statistics (Market Cap, PE Ratio, etc.), and a mini-chart.
- **Financials**: Historical Revenue, Net Income, and Balance Sheet data.
- **History**: Detailed historical price charts and data tables.
- **Dividends**: History of dividend payments and yields.
- **Forecast**: Analyst recommendations and price targets.
- **Profile**: Company description, sector, industry, and corporate information.
- **News**: Latest news articles specifically related to the company.

## 2. Current Infrastructure (What we have)
The following components are already implemented and will be reused:
- **`MarketData` Model**: Stores current price, market cap, PE ratio, sector, industry, description, logo, and website.
- **`StockPriceHistory` Model**: Stores historical OHLCV data for charts.
- **`AnalystRecommendation` Model**: Stores price targets and buy/sell ratings.
- **`EarningsCalendar` Model**: Stores upcoming and past earnings dates.
- **`Dividend` Model**: Stores dividend history and announcements.
- **`NewsItem` Model**: General news system (needs symbol linking).
- **Public API**: `/api/stocks/profile/<symbol>` (needs expansion).

## 3. Database Schema Requirements

### 3.1 New Tables
#### `company_financials`
Stores historical financial statements to power the **Financials** and **Metrics** tabs.
- `symbol` (String, Index): The ticker symbol.
- `period` (Enum: 'annual', 'quarterly'): The reporting frequency.
- `fiscal_date_ending` (Date): The end date of the reporting period.
- `revenue`, `net_income`, `gross_profit`, `ebitda` (BigInteger): Income statement items.
- `total_assets`, `total_liabilities`, `shareholder_equity` (BigInteger): Balance sheet items.
- `eps_actual`, `eps_estimate` (Numeric): Earnings per share data.

#### `market_issues`
Stores regulatory alerts, market warnings, or corporate governance notes.
- `symbol` (String, Index): The ticker symbol.
- `title` (String): Short summary of the issue.
- `description` (Text): Detailed explanation.
- `severity` (Enum: 'info', 'warning', 'critical'): Importance level.
- `issue_date` (Date): When the issue was recorded.
- `is_active` (Boolean): Whether the issue is currently relevant.

### 3.2 Table Modifications
#### `market_data`
- Add `is_listed` (Boolean, default=False): Controls visibility in the public Business Directory.
- Add `is_featured` (Boolean, default=False): For highlighting specific companies on the dashboard.

#### `news_items`
- Add `related_symbol` (String, Index): To link news articles directly to a specific company profile.

## 4. Admin Panel Features
The Admin Panel will serve as the control center for the Business Directory:
- **Business Directory Management**: A list view of all stocks with a toggle to "List" or "Unlist" them from the public profile section.
- **Profile Editor**: Interface to manually refine company descriptions, logos, and contact information.
- **Financial Data Sync**: A tool to trigger `yfinance` API calls to fetch and populate the `company_financials` table for a specific symbol.
- **Issue Manager**: Interface to add, edit, or resolve `market_issues` for any company.

## 5. Public API Enhancements
### Updated Endpoint: `GET /api/stocks/profile/<symbol>`
The response will be expanded to aggregate data from multiple tables:
- `overview`: Current market stats (from `MarketData`).
- `financials`: Historical revenue/income trends (from `company_financials`).
- `news`: Latest 5-10 articles (from `news_items` where `related_symbol` matches).
- `issues`: Active alerts (from `market_issues`).
- `forecast`: Analyst targets and recommendations (from `AnalystRecommendation`).

## 6. Implementation Roadmap

### Phase 1: Database & Models (The Foundation)
1. Define `CompanyFinancials` and `MarketIssue` models in `models/market.py`.
2. Add `is_listed` and `is_featured` to `MarketData`.
3. Add `related_symbol` to `NewsItem`.
4. Generate and run database migrations.

### Phase 2: Admin Backend (The Data Source)
1. Create admin routes for managing the Business Directory.
2. Implement the `yfinance` handler to fetch and store historical financials.
3. Create CRUD routes for `MarketIssue`.

### Phase 3: Public API (The Delivery)
1. Update the `/api/stocks/profile/<symbol>` route to fetch and return the new aggregated data structure.
2. Ensure the API supports the "X-User-Country" filtering logic already present in the system.

### Phase 4: Frontend UI (The Visuals)
1. Implement the tabbed navigation (Overview, Financials, History, etc.).
2. Build the data visualization components (Financial charts, News feeds, Issue alerts).
