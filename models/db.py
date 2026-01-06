"""
SQLAlchemy Database Configuration and Models
PeartoFinance Backend
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# ============== USER MODELS ==============

class User(db.Model):
    """User accounts table"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default='user')
    avatar_url = db.Column(db.String(500))
    country_code = db.Column(db.String(10), default='US')
    phone = db.Column(db.String(50))
    dob = db.Column(db.Date)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'avatarUrl': self.avatar_url,
            'countryCode': self.country_code,
            'isVerified': self.is_verified
        }


class PasswordResetToken(db.Model):
    """Password reset tokens"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============== MARKET DATA MODELS ==============

class MarketPrice(db.Model):
    """Real-time market prices for stocks, crypto, forex"""
    __tablename__ = 'market_prices'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(255))
    price = db.Column(db.Numeric(18, 4))
    change_amount = db.Column(db.Numeric(18, 4))
    change_percent = db.Column(db.Numeric(10, 4))
    volume = db.Column(db.BigInteger)
    market_cap = db.Column(db.BigInteger)
    high_52w = db.Column(db.Numeric(18, 4))
    low_52w = db.Column(db.Numeric(18, 4))
    ytd_change = db.Column(db.Numeric(10, 4))
    sector = db.Column(db.String(100))
    exchange = db.Column(db.String(50))
    asset_type = db.Column(db.String(20), default='stock')  # stock, crypto, forex
    country_code = db.Column(db.String(10), default='US')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'change': float(self.change_amount) if self.change_amount else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'volume': self.volume,
            'marketCap': self.market_cap,
            'high52w': float(self.high_52w) if self.high_52w else None,
            'low52w': float(self.low_52w) if self.low_52w else None,
            'sector': self.sector,
            'exchange': self.exchange
        }


class StockProfile(db.Model):
    """Company profiles for stocks"""
    __tablename__ = 'stock_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, unique=True)
    name = db.Column(db.String(255))
    description = db.Column(db.Text)
    ceo = db.Column(db.String(255))
    employees = db.Column(db.Integer)
    headquarters = db.Column(db.String(255))
    founded = db.Column(db.String(10))
    website = db.Column(db.String(255))
    sector = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    exchange = db.Column(db.String(50))
    country_code = db.Column(db.String(10))
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'description': self.description,
            'ceo': self.ceo,
            'employees': self.employees,
            'headquarters': self.headquarters,
            'founded': self.founded,
            'website': self.website,
            'sector': self.sector,
            'industry': self.industry,
            'exchange': self.exchange
        }


class StockHistory(db.Model):
    """Historical stock prices"""
    __tablename__ = 'stock_history'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False)
    open = db.Column(db.Numeric(18, 4))
    high = db.Column(db.Numeric(18, 4))
    low = db.Column(db.Numeric(18, 4))
    close = db.Column(db.Numeric(18, 4))
    volume = db.Column(db.BigInteger)
    
    def to_dict(self):
        return {
            'date': self.date.strftime('%Y-%m-%d') if self.date else None,
            'open': float(self.open) if self.open else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None,
            'close': float(self.close) if self.close else None,
            'volume': self.volume
        }


# ============== CRYPTO MODELS ==============

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
            'marketCapChange24h': float(self.market_cap_change_24h) if self.market_cap_change_24h else None
        }


# ============== NEWS MODELS ==============

class Article(db.Model):
    """News articles"""
    __tablename__ = 'curated_articles'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(255))
    summary = db.Column(db.Text)
    content = db.Column(db.Text)
    canonical_url = db.Column(db.String(500))
    image = db.Column(db.String(500))
    source = db.Column(db.String(100))
    source_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    curated_status = db.Column(db.String(50), default='draft')
    featured = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10), default='US')
    published_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'summary': self.summary,
            'url': self.canonical_url,
            'image': self.image,
            'source': self.source,
            'category': self.category,
            'featured': self.featured,
            'publishedAt': self.published_at.isoformat() if self.published_at else None,
            'country': self.country_code
        }


# ============== EDUCATION MODELS ==============

class Course(db.Model):
    """Educational courses"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255))
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    category = db.Column(db.String(100))
    level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced'), default='Beginner')
    duration_weeks = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))
    thumbnail_url = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=False)
    enrollment_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'durationWeeks': self.duration_weeks,
            'price': float(self.price) if self.price else None,
            'thumbnailUrl': self.thumbnail_url,
            'isPublished': self.is_published,
            'enrollmentCount': self.enrollment_count,
            'rating': float(self.rating) if self.rating else None
        }


class Instructor(db.Model):
    """Course instructors"""
    __tablename__ = 'instructors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.String(500))
    expertise = db.Column(db.Text)
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    course_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============== COUNTRY MODELS ==============

class Country(db.Model):
    """Supported countries"""
    __tablename__ = 'countries'
    
    code = db.Column(db.String(2), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    native_name = db.Column(db.String(100))
    currency_code = db.Column(db.String(3))
    currency_symbol = db.Column(db.String(10))
    currency_name = db.Column(db.String(50))
    default_market_index = db.Column(db.String(50))
    timezone = db.Column(db.String(50))
    flag_emoji = db.Column(db.String(10))
    phone_code = db.Column(db.String(10))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'code': self.code,
            'name': self.name,
            'nativeName': self.native_name,
            'currencyCode': self.currency_code,
            'currencySymbol': self.currency_symbol,
            'flagEmoji': self.flag_emoji,
            'defaultMarketIndex': self.default_market_index
        }


# ============== PORTFOLIO MODELS ==============

class Portfolio(db.Model):
    """User portfolios"""
    __tablename__ = 'portfolios'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='My Portfolio')
    description = db.Column(db.Text)
    is_default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortfolioItem(db.Model):
    """Portfolio holdings"""
    __tablename__ = 'portfolio_items'
    
    id = db.Column(db.String(255), primary_key=True)
    portfolio_id = db.Column(db.String(255), db.ForeignKey('portfolios.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    shares = db.Column(db.Numeric(18, 8))
    buy_price = db.Column(db.Numeric(18, 4))
    buy_date = db.Column(db.Date)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Watchlist(db.Model):
    """User watchlists"""
    __tablename__ = 'watchlists'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.String(255), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(255), default='My Watchlist')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WatchlistItem(db.Model):
    """Watchlist items"""
    __tablename__ = 'watchlist_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    watchlist_id = db.Column(db.String(255), db.ForeignKey('watchlists.id'), nullable=False)
    symbol = db.Column(db.String(20), nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)


# ============== FAQ/GLOSSARY MODELS ==============

class FAQ(db.Model):
    """Frequently asked questions"""
    __tablename__ = 'faqs'
    
    id = db.Column(db.String(50), primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    show_on_homepage = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GlossaryTerm(db.Model):
    """Financial glossary terms"""
    __tablename__ = 'glossary_terms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum('trading', 'investing', 'derivatives', 'banking', 'crypto', 'economics', 'technical'))
    related_terms = db.Column(db.JSON)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'definition': self.definition,
            'category': self.category,
            'relatedTerms': self.related_terms
        }


# ============== COMMODITIES MODELS ==============

class CommodityData(db.Model):
    """Commodities market data"""
    __tablename__ = 'commodities_data'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(20), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Numeric(15, 4))
    change_amount = db.Column(db.Numeric(15, 4))
    change_percent = db.Column(db.Numeric(10, 4))
    previous_close = db.Column(db.Numeric(15, 4))
    day_high = db.Column(db.Numeric(15, 4))
    day_low = db.Column(db.Numeric(15, 4))
    category = db.Column(db.Enum('precious_metals', 'energy', 'agriculture', 'industrial_metals', 'other'))
    unit = db.Column(db.String(20))
    currency = db.Column(db.String(10), default='USD')
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'symbol': self.symbol,
            'name': self.name,
            'price': float(self.price) if self.price else None,
            'change': float(self.change_amount) if self.change_amount else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'category': self.category,
            'unit': self.unit
        }
