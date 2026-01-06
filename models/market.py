"""
Market Data Models (Stocks, Crypto, Forex, Commodities)
PeartoFinance Backend - Matches actual database schema
"""
from datetime import datetime
from .base import db


class MarketData(db.Model):
    """General market data - matches sina_finance.market_data table exactly"""
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
    asset_type = db.Column(db.Enum('stock', 'crypto', 'forex', 'commodity', 'index'), default='stock')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    country_code = db.Column(db.String(2), default='US')
    
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
            'countryCode': self.country_code
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
    country_code = db.Column(db.String(5), default='US')
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
            'currency': self.currency
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
    """Stock offerings (IPO, FPO, etc.)"""
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
