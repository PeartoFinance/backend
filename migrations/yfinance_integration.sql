-- YFinance Integration Database Migration
-- Adds new tables and columns for enhanced market data support
-- Run this migration after the existing schema is in place

-- ============================================================================
-- ADD NEW COLUMNS TO market_data TABLE
-- ============================================================================

ALTER TABLE market_data 
ADD COLUMN IF NOT EXISTS sector VARCHAR(100),
ADD COLUMN IF NOT EXISTS industry VARCHAR(100),
ADD COLUMN IF NOT EXISTS open_price DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS previous_close DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS day_high DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS day_low DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS avg_volume BIGINT,
ADD COLUMN IF NOT EXISTS beta DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS forward_pe DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS trailing_pe DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS eps DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS dividend_yield DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS dividend_rate DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS book_value DECIMAL(18, 6),
ADD COLUMN IF NOT EXISTS price_to_book DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS shares_outstanding BIGINT,
ADD COLUMN IF NOT EXISTS float_shares BIGINT,
ADD COLUMN IF NOT EXISTS short_ratio DECIMAL(10, 4),
ADD COLUMN IF NOT EXISTS logo_url VARCHAR(500),
ADD COLUMN IF NOT EXISTS website VARCHAR(255),
ADD COLUMN IF NOT EXISTS description TEXT;

-- ============================================================================
-- ADD NEW COLUMNS TO stock_offers TABLE
-- ============================================================================

ALTER TABLE stock_offers
ADD COLUMN IF NOT EXISTS exchange VARCHAR(50),
ADD COLUMN IF NOT EXISTS deal_type VARCHAR(50),
ADD COLUMN IF NOT EXISTS shares_offered BIGINT,
ADD COLUMN IF NOT EXISTS offer_price DECIMAL(18, 6);

-- ============================================================================
-- CREATE stock_price_history TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS stock_price_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    date DATE NOT NULL,
    open_price DECIMAL(18, 6),
    high DECIMAL(18, 6),
    low DECIMAL(18, 6),
    close DECIMAL(18, 6),
    adj_close DECIMAL(18, 6),
    volume BIGINT,
    `interval` VARCHAR(10) DEFAULT '1d',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_date (date),
    UNIQUE KEY uq_symbol_date_interval (symbol, date, `interval`)
);

-- ============================================================================
-- CREATE earnings_calendar TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS earnings_calendar (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    earnings_date DATETIME NOT NULL,
    eps_estimate DECIMAL(18, 6),
    eps_actual DECIMAL(18, 6),
    surprise_percent DECIMAL(10, 4),
    revenue_estimate BIGINT,
    revenue_actual BIGINT,
    market_cap BIGINT,
    before_after_market VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_earnings_date (earnings_date)
);

-- ============================================================================
-- CREATE analyst_recommendations TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS analyst_recommendations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    firm VARCHAR(100),
    to_grade VARCHAR(50),
    from_grade VARCHAR(50),
    action VARCHAR(50),
    date DATE,
    target_high DECIMAL(18, 6),
    target_low DECIMAL(18, 6),
    target_mean DECIMAL(18, 6),
    target_median DECIMAL(18, 6),
    current_price DECIMAL(18, 6),
    strong_buy INT DEFAULT 0,
    buy INT DEFAULT 0,
    hold INT DEFAULT 0,
    sell INT DEFAULT 0,
    strong_sell INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_date (date)
);

-- ============================================================================
-- CREATE stock_splits TABLE
-- ============================================================================

CREATE TABLE IF NOT EXISTS stock_splits (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(255),
    split_date DATE NOT NULL,
    split_ratio VARCHAR(20),
    numerator INT,
    denominator INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_symbol (symbol),
    INDEX idx_split_date (split_date)
);

-- ============================================================================
-- VERIFY MIGRATION
-- ============================================================================

-- Check tables exist
SELECT 'Migration complete!' AS status;
