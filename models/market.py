"""
Market Data Models (Stocks, Crypto, Forex, Commodities)
PeartoFinance Backend - Enhanced for yfinance integration
"""
from datetime import datetime
from .base import db


class MarketData(db.Model):
    """General market data - enhanced for yfinance integration"""
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Numeric(18, 6))
    change = db.Column(db.Numeric(18, 6))
    change_percent = db.Column(db.Numeric(10, 4))
    volume = db.Column(db.BigInteger)
    market_cap = db.Column(db.BigInteger)
    pe_ratio = db.Column(db.Numeric(10, 4))
    # Note: SQL uses 52_week_high but Python can't have variable starting with number
    # Using _ prefix for these columns
    _52_week_high = db.Column('52_week_high', db.Numeric(18, 6))
    _52_week_low = db.Column('52_week_low', db.Numeric(18, 6))
    currency = db.Column(db.String(3), default='USD')
    exchange = db.Column(db.String(50))
    asset_type = db.Column(db.Enum('stock', 'crypto', 'forex', 'commodity', 'index', 'etf'), default='stock')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    country_code = db.Column(db.String(10), default='US')
    
    # Additional fields for yfinance data
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    open_price = db.Column(db.Numeric(18, 6))
    previous_close = db.Column(db.Numeric(18, 6))
    day_high = db.Column(db.Numeric(18, 6))
    day_low = db.Column(db.Numeric(18, 6))
    avg_volume = db.Column(db.BigInteger)
    beta = db.Column(db.Numeric(10, 4))
    forward_pe = db.Column(db.Numeric(10, 4))
    trailing_pe = db.Column(db.Numeric(10, 4))
    eps = db.Column(db.Numeric(18, 6))
    dividend_yield = db.Column(db.Numeric(10, 4))
    dividend_rate = db.Column(db.Numeric(18, 6))
    book_value = db.Column(db.Numeric(18, 6))
    price_to_book = db.Column(db.Numeric(10, 4))
    shares_outstanding = db.Column(db.BigInteger)
    float_shares = db.Column(db.BigInteger)
    short_ratio = db.Column(db.Numeric(10, 4))
    logo_url = db.Column(db.String(500))
    website = db.Column(db.String(255))
    description = db.Column(db.Text)
    ytd_return = db.Column(db.Numeric(10, 4)) # Year-to-Date return percentage
    
    # Business Profile Features (Added for detailed company profiles)
    is_listed = db.Column(db.Boolean, default=False, index=True) # Controls visibility in public directory
    is_featured = db.Column(db.Boolean, default=False) # For highlighting on dashboard
    
    __table_args__ = (
        db.UniqueConstraint('symbol', 'country_code', 'asset_type', name='uq_market_data_symbol_country_asset'),
        # Performance indexes for sorting and filtering
        db.Index('idx_market_movers', 'asset_type', 'is_listed', 'change_percent'),
        db.Index('idx_market_volume', 'asset_type', 'is_listed', 'volume'),
        db.Index('idx_market_country', 'country_code', 'asset_type'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'change': float(self.change) if self.change else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'volume': self.volume,
            'marketCap': self.market_cap,
            'peRatio': float(self.pe_ratio) if self.pe_ratio else None,
            'high52w': float(self._52_week_high) if self._52_week_high else None,
            'low52w': float(self._52_week_low) if self._52_week_low else None,
            'currency': self.currency,
            'exchange': self.exchange,
            'assetType': self.asset_type,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None,
            'countryCode': self.country_code,
            # Additional fields
            'sector': self.sector,
            'industry': self.industry,
            'open': float(self.open_price) if self.open_price else None,
            'previousClose': float(self.previous_close) if self.previous_close else None,
            'dayHigh': float(self.day_high) if self.day_high else None,
            'dayLow': float(self.day_low) if self.day_low else None,
            'avgVolume': self.avg_volume,
            'beta': float(self.beta) if self.beta else None,
            'forwardPe': float(self.forward_pe) if self.forward_pe else None,
            'trailingPe': float(self.trailing_pe) if self.trailing_pe else None,
            'eps': float(self.eps) if self.eps else None,
            'dividendYield': float(self.dividend_yield) if self.dividend_yield else None,
            'dividendRate': float(self.dividend_rate) if self.dividend_rate else None,
            'bookValue': float(self.book_value) if self.book_value else None,
            'priceToBook': float(self.price_to_book) if self.price_to_book else None,
            'sharesOutstanding': self.shares_outstanding,
            'floatShares': self.float_shares,
            'shortRatio': float(self.short_ratio) if self.short_ratio else None,
            'logoUrl': self.logo_url,
            'website': self.website,
            'description': self.description,
            'isListed': self.is_listed,
            'isFeatured': self.is_featured,
            'ytdReturn': float(self.ytd_return) if self.ytd_return else None,
        }



class MarketIndices(db.Model):
    """Major market indices - matches sina_finance.market_indices exactly"""
    __tablename__ = 'market_indices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(15, 4))
    change_amount = db.Column(db.Numeric(15, 4))
    change_percent = db.Column(db.Numeric(10, 4))
    previous_close = db.Column(db.Numeric(15, 4))
    day_high = db.Column(db.Numeric(15, 4))
    day_low = db.Column(db.Numeric(15, 4))
    year_high = db.Column(db.Numeric(15, 4))
    year_low = db.Column(db.Numeric(15, 4))
    market_status = db.Column(db.Enum('pre-market', 'open', 'after-hours', 'closed'), default='closed')
    country_code = db.Column(db.String(10), default='US')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'value': float(self.price) if self.price else None,
            'change': float(self.change_amount) if self.change_amount else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'previousClose': float(self.previous_close) if self.previous_close else None,
            'dayHigh': float(self.day_high) if self.day_high else None,
            'dayLow': float(self.day_low) if self.day_low else None,
            'yearHigh': float(self.year_high) if self.year_high else None,
            'yearLow': float(self.year_low) if self.year_low else None,
            'marketStatus': self.market_status,
            'countryCode': self.country_code,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None
        }


class MarketCache(db.Model):
    """Cached market data responses"""
    __tablename__ = 'market_cache'
    
    id = db.Column(db.String(255), primary_key=True)
    cache_key = db.Column(db.String(255), unique=True, nullable=False)
    data = db.Column(db.JSON)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class MarketSentiment(db.Model):
    """Market sentiment indicators"""
    __tablename__ = 'market_sentiment'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    indicator_type = db.Column(db.Enum('fear_greed', 'vix', 'put_call_ratio', 'other'), default='fear_greed')
    value = db.Column(db.Numeric(10, 2), nullable=False)
    classification = db.Column(db.String(50))
    previous_close = db.Column(db.Numeric(10, 2))
    previous_week = db.Column(db.Numeric(10, 2))
    previous_month = db.Column(db.Numeric(10, 2))
    previous_year = db.Column(db.Numeric(10, 2))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class CryptoMarketData(db.Model):
    """Global cryptocurrency market data"""
    __tablename__ = 'crypto_market_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    total_market_cap = db.Column(db.Numeric(20, 2))
    total_volume_24h = db.Column(db.Numeric(20, 2))
    btc_dominance = db.Column(db.Numeric(10, 4))
    eth_dominance = db.Column(db.Numeric(10, 4))
    active_cryptocurrencies = db.Column(db.Integer)
    active_exchanges = db.Column(db.Integer)
    market_cap_change_24h = db.Column(db.Numeric(10, 4))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'totalMarketCap': float(self.total_market_cap) if self.total_market_cap else None,
            'totalVolume24h': float(self.total_volume_24h) if self.total_volume_24h else None,
            'btcDominance': float(self.btc_dominance) if self.btc_dominance else None,
            'ethDominance': float(self.eth_dominance) if self.eth_dominance else None,
            'activeCryptocurrencies': self.active_cryptocurrencies,
            'activeExchanges': self.active_exchanges,
            'marketCapChange24h': float(self.market_cap_change_24h) if self.market_cap_change_24h else None,
            'lastUpdated': self.last_updated.isoformat() if self.last_updated else None
        }


class CommodityData(db.Model):
    """Commodities market data"""
    __tablename__ = 'commodities_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100))
    price = db.Column(db.Numeric(18, 6))
    change = db.Column(db.Numeric(18, 6))
    change_percent = db.Column(db.Numeric(10, 4))
    day_high = db.Column(db.Numeric(18, 6))
    day_low = db.Column(db.Numeric(18, 6))
    year_high = db.Column(db.Numeric(18, 6))
    year_low = db.Column(db.Numeric(18, 6))
    unit = db.Column(db.String(20))
    currency = db.Column(db.String(10), default='USD')
    country_code = db.Column(db.String(10), default='GLOBAL')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'change': float(self.change) if self.change else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'dayHigh': float(self.day_high) if self.day_high else None,
            'dayLow': float(self.day_low) if self.day_low else None,
            'unit': self.unit,
            'currency': self.currency,
            'countryCode': self.country_code
        }


class EconomicEvent(db.Model):
    """Economic calendar events"""
    __tablename__ = 'economic_events'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    country = db.Column(db.String(50))
    event_date = db.Column(db.DateTime)
    importance = db.Column(db.Enum('low', 'medium', 'high'))
    forecast = db.Column(db.String(50))
    previous = db.Column(db.String(50))
    actual = db.Column(db.String(50))
    currency = db.Column(db.String(10))
    source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'country': self.country,
            'eventDate': self.event_date.isoformat() if self.event_date else None,
            'importance': self.importance,
            'forecast': self.forecast,
            'previous': self.previous,
            'actual': self.actual,
            'currency': self.currency,
            'source': self.source
        }


class StockOffer(db.Model):
    """Stock offerings (IPO, FPO, etc.) - enhanced for yfinance IPO calendar"""
    __tablename__ = 'stock_offers'
    
    id = db.Column(db.String(255), primary_key=True)
    symbol = db.Column(db.String(20))
    company_name = db.Column(db.String(255))
    offer_type = db.Column(db.Enum('ipo', 'fpo', 'rights'))
    price_range = db.Column(db.String(50))
    units = db.Column(db.BigInteger)
    min_application = db.Column(db.Integer)
    open_date = db.Column(db.Date)
    close_date = db.Column(db.Date)
    listing_date = db.Column(db.Date)
    status = db.Column(db.Enum('upcoming', 'open', 'closed', 'listed'))
    prospectus_url = db.Column(db.Text)
    country_code = db.Column(db.String(10))
    exchange = db.Column(db.String(50))
    deal_type = db.Column(db.String(50))  # From yfinance: 'Priced', 'Filed', etc.
    shares_offered = db.Column(db.BigInteger)
    offer_price = db.Column(db.Numeric(18, 6))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'companyName': self.company_name,
            'offerType': self.offer_type,
            'priceRange': self.price_range,
            'units': self.units,
            'openDate': self.open_date.isoformat() if self.open_date else None,
            'closeDate': self.close_date.isoformat() if self.close_date else None,
            'listingDate': self.listing_date.isoformat() if self.listing_date else None,
            'status': self.status,
            'exchange': self.exchange,
            'dealType': self.deal_type,
            'sharesOffered': self.shares_offered,
            'offerPrice': float(self.offer_price) if self.offer_price else None,
        }


class StockPriceHistory(db.Model):
    """Historical OHLCV price data from yfinance"""
    __tablename__ = 'stock_price_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    open_price = db.Column(db.Numeric(18, 6))
    high = db.Column(db.Numeric(18, 6))
    low = db.Column(db.Numeric(18, 6))
    close = db.Column(db.Numeric(18, 6))
    adj_close = db.Column(db.Numeric(18, 6))
    volume = db.Column(db.BigInteger)
    interval = db.Column(db.String(10), default='1d')  # 1d, 1h, 5m, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('symbol', 'date', 'interval', name='uq_symbol_date_interval'),
    )

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'date': self.date.isoformat() if self.date else None,
            'open': float(self.open_price) if self.open_price else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'adjClose': float(self.adj_close) if self.adj_close else None,
            'volume': self.volume,
            'interval': self.interval,
        }


class EarningsCalendar(db.Model):
    """Earnings calendar events from yfinance"""
    __tablename__ = 'earnings_calendar'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    earnings_date = db.Column(db.DateTime, nullable=False)
    eps_estimate = db.Column(db.Numeric(18, 6))
    eps_actual = db.Column(db.Numeric(18, 6))
    surprise_percent = db.Column(db.Numeric(10, 4))
    revenue_estimate = db.Column(db.BigInteger)
    revenue_actual = db.Column(db.BigInteger)
    market_cap = db.Column(db.BigInteger)
    before_after_market = db.Column(db.String(20))  # 'BMO', 'AMC', 'TNS'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'companyName': self.company_name,
            'earningsDate': self.earnings_date.isoformat() if self.earnings_date else None,
            'epsEstimate': float(self.eps_estimate) if self.eps_estimate else None,
            'epsActual': float(self.eps_actual) if self.eps_actual else None,
            'surprisePercent': float(self.surprise_percent) if self.surprise_percent else None,
            'revenueEstimate': self.revenue_estimate,
            'revenueActual': self.revenue_actual,
            'marketCap': self.market_cap,
            'beforeAfterMarket': self.before_after_market,
        }


class AnalystRecommendation(db.Model):
    """Analyst recommendations and price targets from yfinance"""
    __tablename__ = 'analyst_recommendations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    firm = db.Column(db.String(100))
    to_grade = db.Column(db.String(50))  # 'Buy', 'Hold', 'Sell', etc.
    from_grade = db.Column(db.String(50))
    action = db.Column(db.String(50))  # 'up', 'down', 'main', 'init'
    date = db.Column(db.Date)
    # Price targets
    target_high = db.Column(db.Numeric(18, 6))
    target_low = db.Column(db.Numeric(18, 6))
    target_mean = db.Column(db.Numeric(18, 6))
    target_median = db.Column(db.Numeric(18, 6))
    current_price = db.Column(db.Numeric(18, 6))
    # Summary counts
    strong_buy = db.Column(db.Integer, default=0)
    buy = db.Column(db.Integer, default=0)
    hold = db.Column(db.Integer, default=0)
    sell = db.Column(db.Integer, default=0)
    strong_sell = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'firm': self.firm,
            'toGrade': self.to_grade,
            'fromGrade': self.from_grade,
            'action': self.action,
            'date': self.date.isoformat() if self.date else None,
            'targetHigh': float(self.target_high) if self.target_high else None,
            'targetLow': float(self.target_low) if self.target_low else None,
            'targetMean': float(self.target_mean) if self.target_mean else None,
            'targetMedian': float(self.target_median) if self.target_median else None,
            'currentPrice': float(self.current_price) if self.current_price else None,
            'strongBuy': self.strong_buy,
            'buy': self.buy,
            'hold': self.hold,
            'sell': self.sell,
            'strongSell': self.strong_sell,
        }


class EarningsEstimate(db.Model):
    """Analyst earnings and revenue estimates for future fiscal periods"""
    __tablename__ = 'earnings_estimates'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    period_type = db.Column(db.String(20), default='annual')  # 'annual' or 'quarterly'
    fiscal_year = db.Column(db.String(10))  # e.g., 'FY2024', 'Q1 2025'
    fiscal_end_date = db.Column(db.Date)
    
    # Revenue Estimates
    revenue_estimate = db.Column(db.BigInteger)  # Mean estimate
    revenue_low = db.Column(db.BigInteger)
    revenue_high = db.Column(db.BigInteger)
    revenue_avg = db.Column(db.BigInteger)
    revenue_growth = db.Column(db.Numeric(10, 4))  # as decimal, e.g., 0.1234 = 12.34%
    num_revenue_analysts = db.Column(db.Integer)
    
    # EPS Estimates
    eps_estimate = db.Column(db.Numeric(18, 6))  # Mean estimate
    eps_low = db.Column(db.Numeric(18, 6))
    eps_high = db.Column(db.Numeric(18, 6))
    eps_avg = db.Column(db.Numeric(18, 6))
    eps_growth = db.Column(db.Numeric(10, 4))  # as decimal
    num_eps_analysts = db.Column(db.Integer)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('symbol', 'period_type', 'fiscal_year', name='uq_earnings_estimate'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'periodType': self.period_type,
            'fiscalYear': self.fiscal_year,
            'fiscalEndDate': self.fiscal_end_date.isoformat() if self.fiscal_end_date else None,
            'revenueEstimate': self.revenue_estimate,
            'revenueLow': self.revenue_low,
            'revenueHigh': self.revenue_high,
            'revenueAvg': self.revenue_avg,
            'revenueGrowth': float(self.revenue_growth) if self.revenue_growth else None,
            'numRevenueAnalysts': self.num_revenue_analysts,
            'epsEstimate': float(self.eps_estimate) if self.eps_estimate else None,
            'epsLow': float(self.eps_low) if self.eps_low else None,
            'epsHigh': float(self.eps_high) if self.eps_high else None,
            'epsAvg': float(self.eps_avg) if self.eps_avg else None,
            'epsGrowth': float(self.eps_growth) if self.eps_growth else None,
            'numEpsAnalysts': self.num_eps_analysts,
        }


class RecommendationHistory(db.Model):
    """Historical analyst recommendation counts for trends chart"""
    __tablename__ = 'recommendation_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    period_date = db.Column(db.Date, nullable=False)  # Month start date
    period_label = db.Column(db.String(20))  # e.g., 'Jan 2025', 'Feb 2025'
    
    strong_buy = db.Column(db.Integer, default=0)
    buy = db.Column(db.Integer, default=0)
    hold = db.Column(db.Integer, default=0)
    sell = db.Column(db.Integer, default=0)
    strong_sell = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('symbol', 'period_date', name='uq_rec_history'),
    )

    def to_dict(self):
        return {
            'symbol': self.symbol,
            'periodDate': self.period_date.isoformat() if self.period_date else None,
            'periodLabel': self.period_label,
            'strongBuy': self.strong_buy,
            'buy': self.buy,
            'hold': self.hold,
            'sell': self.sell,
            'strongSell': self.strong_sell,
        }


class StockSplit(db.Model):
    """Stock split events from yfinance calendar"""
    __tablename__ = 'stock_splits'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    split_date = db.Column(db.Date, nullable=False)
    split_ratio = db.Column(db.String(20))  # e.g., '4:1', '2:1'
    numerator = db.Column(db.Integer)
    denominator = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'companyName': self.company_name,
            'splitDate': self.split_date.isoformat() if self.split_date else None,
            'splitRatio': self.split_ratio,
            'numerator': self.numerator,
            'denominator': self.denominator,
        }


class Dividend(db.Model):
    """Proposed dividend announcements"""
    __tablename__ = 'dividends'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    dividend_type = db.Column(db.Enum('cash', 'bonus', 'both'), default='cash')
    cash_percent = db.Column(db.Numeric(10, 4), default=0)
    bonus_percent = db.Column(db.Numeric(10, 4), default=0)
    total_percent = db.Column(db.Numeric(10, 4), default=0)
    dividend_amount = db.Column(db.Numeric(18, 6))  # Per share amount
    ex_dividend_date = db.Column(db.Date)
    record_date = db.Column(db.Date)
    payment_date = db.Column(db.Date)
    book_closure_date = db.Column(db.Date)
    fiscal_year = db.Column(db.String(20))
    status = db.Column(db.Enum('proposed', 'approved', 'paid'), default='proposed')
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'companyName': self.company_name,
            'dividendType': self.dividend_type,
            'cashPercent': float(self.cash_percent) if self.cash_percent else 0,
            'bonusPercent': float(self.bonus_percent) if self.bonus_percent else 0,
            'totalPercent': float(self.total_percent) if self.total_percent else 0,
            'dividendAmount': float(self.dividend_amount) if self.dividend_amount else None,
            'exDividendDate': self.ex_dividend_date.isoformat() if self.ex_dividend_date else None,
            'recordDate': self.record_date.isoformat() if self.record_date else None,
            'paymentDate': self.payment_date.isoformat() if self.payment_date else None,
            'bookClosureDate': self.book_closure_date.isoformat() if self.book_closure_date else None,
            'fiscalYear': self.fiscal_year,
            'status': self.status,
        }


class BulkTransaction(db.Model):
    """Bulk/block transactions - large institutional trades"""
    __tablename__ = 'bulk_transactions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    company_name = db.Column(db.String(255))
    transaction_date = db.Column(db.DateTime, default=datetime.utcnow)
    buyer_broker = db.Column(db.Integer)  # Broker number
    seller_broker = db.Column(db.Integer)  # Broker number
    quantity = db.Column(db.BigInteger)
    price = db.Column(db.Numeric(18, 6))
    amount = db.Column(db.Numeric(20, 2))  # Total transaction value
    change_percent = db.Column(db.Numeric(10, 4))
    transaction_type = db.Column(db.Enum('bulk', 'block', 'cross'), default='bulk')
    exchange = db.Column(db.String(50))
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'companyName': self.company_name,
            'transactionDate': self.transaction_date.isoformat() if self.transaction_date else None,
            'buyerBroker': self.buyer_broker,
            'sellerBroker': self.seller_broker,
            'quantity': self.quantity,
            'price': float(self.price) if self.price else None,
            'amount': float(self.amount) if self.amount else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'transactionType': self.transaction_type,
            'exchange': self.exchange,
        }


class CompanyFinancials(db.Model):
    """Historical financial statements for Business Profiles - Enhanced for StockAnalysis-style display"""
    __tablename__ = 'company_financials'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    period = db.Column(db.Enum('annual', 'quarterly', 'ttm'), default='annual')
    fiscal_date_ending = db.Column(db.Date, nullable=False)
    
    # =========================================================================
    # INCOME STATEMENT
    # =========================================================================
    revenue = db.Column(db.BigInteger)
    cost_of_revenue = db.Column(db.BigInteger)
    gross_profit = db.Column(db.BigInteger)
    selling_general_admin = db.Column(db.BigInteger)
    research_development = db.Column(db.BigInteger)
    operating_expenses = db.Column(db.BigInteger)
    operating_income = db.Column(db.BigInteger)
    interest_expense = db.Column(db.BigInteger)
    interest_income = db.Column(db.BigInteger)
    pretax_income = db.Column(db.BigInteger)
    income_tax = db.Column(db.BigInteger)
    net_income = db.Column(db.BigInteger)
    net_income_common = db.Column(db.BigInteger)
    ebitda = db.Column(db.BigInteger)
    ebit = db.Column(db.BigInteger)
    
    # Per Share
    eps_basic = db.Column(db.Numeric(18, 6))
    eps_diluted = db.Column(db.Numeric(18, 6))
    shares_basic = db.Column(db.BigInteger)
    shares_diluted = db.Column(db.BigInteger)
    
    # Margins (stored as percentages, e.g., 45.5 for 45.5%)
    gross_margin = db.Column(db.Numeric(10, 4))
    operating_margin = db.Column(db.Numeric(10, 4))
    profit_margin = db.Column(db.Numeric(10, 4))
    
    # =========================================================================
    # BALANCE SHEET
    # =========================================================================
    # Assets
    cash_and_equivalents = db.Column(db.BigInteger)
    short_term_investments = db.Column(db.BigInteger)
    accounts_receivable = db.Column(db.BigInteger)
    inventory = db.Column(db.BigInteger)
    current_assets = db.Column(db.BigInteger)
    property_plant_equipment = db.Column(db.BigInteger)
    long_term_investments = db.Column(db.BigInteger)
    goodwill = db.Column(db.BigInteger)
    intangible_assets = db.Column(db.BigInteger)
    total_assets = db.Column(db.BigInteger)
    
    # Liabilities
    accounts_payable = db.Column(db.BigInteger)
    short_term_debt = db.Column(db.BigInteger)
    current_liabilities = db.Column(db.BigInteger)
    long_term_debt = db.Column(db.BigInteger)
    total_liabilities = db.Column(db.BigInteger)
    total_debt = db.Column(db.BigInteger)
    
    # Equity
    common_stock = db.Column(db.BigInteger)
    retained_earnings = db.Column(db.BigInteger)
    shareholder_equity = db.Column(db.BigInteger)
    
    # Computed Balance Sheet Metrics
    working_capital = db.Column(db.BigInteger)
    net_cash = db.Column(db.BigInteger)  # Cash - Debt
    
    # =========================================================================
    # CASH FLOW
    # =========================================================================
    depreciation_amortization = db.Column(db.BigInteger)
    stock_based_compensation = db.Column(db.BigInteger)
    change_in_working_capital = db.Column(db.BigInteger)
    operating_cash_flow = db.Column(db.BigInteger)
    capital_expenditure = db.Column(db.BigInteger)
    investing_cash_flow = db.Column(db.BigInteger)
    debt_issued = db.Column(db.BigInteger)
    debt_repaid = db.Column(db.BigInteger)
    dividends_paid = db.Column(db.BigInteger)
    stock_repurchased = db.Column(db.BigInteger)
    financing_cash_flow = db.Column(db.BigInteger)
    free_cash_flow = db.Column(db.BigInteger)
    net_cash_flow = db.Column(db.BigInteger)
    
    # =========================================================================
    # META
    # =========================================================================
    currency = db.Column(db.String(10), default='USD')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('symbol', 'period', 'fiscal_date_ending', name='uq_financials_symbol_period_date'),
    )

    def to_dict(self):
        """Full dict for API response"""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'period': self.period,
            'fiscalDateEnding': self.fiscal_date_ending.isoformat() if self.fiscal_date_ending else None,
            # Income Statement
            'revenue': self.revenue,
            'costOfRevenue': self.cost_of_revenue,
            'grossProfit': self.gross_profit,
            'sellingGeneralAdmin': self.selling_general_admin,
            'researchDevelopment': self.research_development,
            'operatingExpenses': self.operating_expenses,
            'operatingIncome': self.operating_income,
            'interestExpense': self.interest_expense,
            'interestIncome': self.interest_income,
            'pretaxIncome': self.pretax_income,
            'incomeTax': self.income_tax,
            'netIncome': self.net_income,
            'netIncomeCommon': self.net_income_common,
            'ebitda': self.ebitda,
            'ebit': self.ebit,
            'epsBasic': float(self.eps_basic) if self.eps_basic else None,
            'epsDiluted': float(self.eps_diluted) if self.eps_diluted else None,
            'sharesBasic': self.shares_basic,
            'sharesDiluted': self.shares_diluted,
            'grossMargin': float(self.gross_margin) if self.gross_margin else None,
            'operatingMargin': float(self.operating_margin) if self.operating_margin else None,
            'profitMargin': float(self.profit_margin) if self.profit_margin else None,
            # Balance Sheet
            'cashAndEquivalents': self.cash_and_equivalents,
            'shortTermInvestments': self.short_term_investments,
            'accountsReceivable': self.accounts_receivable,
            'inventory': self.inventory,
            'currentAssets': self.current_assets,
            'propertyPlantEquipment': self.property_plant_equipment,
            'longTermInvestments': self.long_term_investments,
            'goodwill': self.goodwill,
            'intangibleAssets': self.intangible_assets,
            'totalAssets': self.total_assets,
            'accountsPayable': self.accounts_payable,
            'shortTermDebt': self.short_term_debt,
            'currentLiabilities': self.current_liabilities,
            'longTermDebt': self.long_term_debt,
            'totalLiabilities': self.total_liabilities,
            'totalDebt': self.total_debt,
            'commonStock': self.common_stock,
            'retainedEarnings': self.retained_earnings,
            'shareholderEquity': self.shareholder_equity,
            'workingCapital': self.working_capital,
            'netCash': self.net_cash,
            # Cash Flow
            'depreciationAmortization': self.depreciation_amortization,
            'stockBasedCompensation': self.stock_based_compensation,
            'changeInWorkingCapital': self.change_in_working_capital,
            'operatingCashFlow': self.operating_cash_flow,
            'capitalExpenditure': self.capital_expenditure,
            'investingCashFlow': self.investing_cash_flow,
            'debtIssued': self.debt_issued,
            'debtRepaid': self.debt_repaid,
            'dividendsPaid': self.dividends_paid,
            'stockRepurchased': self.stock_repurchased,
            'financingCashFlow': self.financing_cash_flow,
            'freeCashFlow': self.free_cash_flow,
            'netCashFlow': self.net_cash_flow,
            # Meta
            'currency': self.currency,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def to_summary_dict(self):
        """Compact dict for summary cards"""
        return {
            'fiscalDateEnding': self.fiscal_date_ending.isoformat() if self.fiscal_date_ending else None,
            'period': self.period,
            'revenue': self.revenue,
            'netIncome': self.net_income,
            'grossProfit': self.gross_profit,
            'ebitda': self.ebitda,
            'epsBasic': float(self.eps_basic) if self.eps_basic else None,
            'totalAssets': self.total_assets,
            'freeCashFlow': self.free_cash_flow,
        }


class MarketIssue(db.Model):
    """Regulatory alerts, market warnings, or corporate governance notes"""
    __tablename__ = 'market_issues'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.Enum('info', 'warning', 'critical'), default='info')
    issue_date = db.Column(db.Date, default=datetime.utcnow().date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'symbol': self.symbol,
            'title': self.title,
            'description': self.description,
            'severity': self.severity,
            'issueDate': self.issue_date.isoformat() if self.issue_date else None,
            'isActive': self.is_active
        }
