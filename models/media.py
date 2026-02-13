"""
Media-related Models (TV, Radio)
PeartoFinance Backend - Matches actual pearto database schema
"""
from datetime import datetime
from .base import db


class TVChannel(db.Model):
    """TV channels - matches pearto.tv_channels exactly"""
    __tablename__ = 'tv_channels'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    stream_url = db.Column(db.Text)
    category = db.Column(db.String(100))
    language = db.Column(db.String(50))
    country_code = db.Column(db.String(10))
    is_live = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'logoUrl': self.logo_url,
            'streamUrl': self.stream_url,
            'category': self.category,
            'language': self.language,
            'countryCode': self.country_code,
            'isLive': self.is_live,
            'isPremium': self.is_premium,
            'isActive': self.is_active
        }


class RadioStation(db.Model):
    """Radio stations - matches pearto.radio_stations exactly"""
    __tablename__ = 'radio_stations'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    stream_url = db.Column(db.String(500), nullable=False)
    website_url = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    country = db.Column(db.String(50))
    genre = db.Column(db.String(50))
    language = db.Column(db.String(50))
    description = db.Column(db.Text)
    bitrate = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    listeners_count = db.Column(db.Integer, default=0)
    position = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    country_code = db.Column(db.String(2))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'streamUrl': self.stream_url,
            'websiteUrl': self.website_url,
            'logoUrl': self.logo_url,
            'country': self.country,
            'genre': self.genre,
            'language': self.language,
            'description': self.description,
            'bitrate': self.bitrate,
            'isActive': self.is_active,
            'listenersCount': self.listeners_count
        }


class ForexRate(db.Model):
    """Forex exchange rates"""
    __tablename__ = 'forex_rates'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    base_currency = db.Column(db.String(10), nullable=False)
    target_currency = db.Column(db.String(10), nullable=False)
    rate = db.Column(db.Numeric(18, 6))
    change = db.Column(db.Numeric(18, 6))
    change_percent = db.Column(db.Numeric(10, 4))
    high = db.Column(db.Numeric(18, 6))
    low = db.Column(db.Numeric(18, 6))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'baseCurrency': self.base_currency,
            'targetCurrency': self.target_currency,
            'pair': f"{self.base_currency}/{self.target_currency}",
            'rate': float(self.rate) if self.rate else None,
            'change': float(self.change) if self.change else None,
            'changePercent': float(self.change_percent) if self.change_percent else None,
            'high': float(self.high) if self.high else None,
            'low': float(self.low) if self.low else None
        }


class TrendingTopic(db.Model):
    """Trending topics"""
    __tablename__ = 'trending_topics'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(50))
    rank = db.Column(db.Integer, default=0)
    mentions = db.Column(db.Integer, default=0)
    sentiment = db.Column(db.String(20))
    related_symbols = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    country_code = db.Column(db.String(2))
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'rank': self.rank,
            'mentions': self.mentions,
            'sentiment': self.sentiment,
            'relatedSymbols': self.related_symbols
        }


class SportsEvent(db.Model):
    """Sports events - matches pearto.sports_events"""
    __tablename__ = 'sports_events'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    external_id = db.Column(db.String(100), index=True)  # e.g. "football-12345"
    name = db.Column(db.String(255), nullable=False)
    sport_type = db.Column(db.String(50), index=True)  # football, basketball, etc.
    league = db.Column(db.String(100))
    team_home = db.Column(db.String(100))
    team_away = db.Column(db.String(100))
    score_home = db.Column(db.String(20))
    score_away = db.Column(db.String(20))
    event_date = db.Column(db.DateTime, index=True)
    venue = db.Column(db.String(255))
    status = db.Column(db.String(50), default='scheduled', index=True)  # scheduled, live, completed
    stream_url = db.Column(db.Text)
    thumbnail_url = db.Column(db.Text)
    country_code = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    is_live = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'externalId': self.external_id,
            'name': self.name,
            'sportType': self.sport_type,
            'league': self.league,
            'teamHome': self.team_home,
            'teamAway': self.team_away,
            'scoreHome': self.score_home,
            'scoreAway': self.score_away,
            'eventDate': self.event_date.isoformat() if self.event_date else None,
            'venue': self.venue,
            'status': self.status,
            'streamUrl': self.stream_url,
            'thumbnailUrl': self.thumbnail_url,
            'countryCode': self.country_code,
            'isActive': self.is_active,
            'isLive': self.is_live,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }


class SportsCategory(db.Model):
    """Sports categories configuration (admin controlled)"""
    __tablename__ = 'sports_categories'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False)  # Football, Basketball, etc.
    key = db.Column(db.String(50), nullable=False, unique=True)  # football, basketball
    api_url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50))  # lucide icon name
    is_active = db.Column(db.Boolean, default=False)
    requests_per_day = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
            'apiUrl': self.api_url,
            'icon': self.icon,
            'isActive': self.is_active,
            'requestsPerDay': self.requests_per_day
        }


class UserFavoriteSport(db.Model):
    """User favorite/pinned sports events"""
    __tablename__ = 'user_favorite_sports'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'event_id', name='uq_user_favorite_sport'),
        {'extend_existing': True}
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    event_id = db.Column(db.Integer, db.ForeignKey('sports_events.id', ondelete='CASCADE'), nullable=False, index=True)
    notify_email = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    event = db.relationship('SportsEvent', backref='favorited_by', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'eventId': self.event_id,
            'notifyEmail': self.notify_email,
            'notifyPush': self.notify_push,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'event': self.event.to_dict() if self.event else None
        }
