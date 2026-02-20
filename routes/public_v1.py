"""
Public API v1 Endpoints (API-as-a-Service)
Allows API key holders to access market data
"""
from datetime import datetime
from flask import Blueprint, jsonify
from routes.decorators import api_key_required
from models import (
    MarketData, CryptoMarketData, NewsItem, Course, EconomicEvent, 
    TVChannel, ForexRate, CommodityData, SportsEvent
)

public_v1_bp = Blueprint('public_v1', __name__)

@public_v1_bp.route('/market/quotes/<symbol>', methods=['GET'])
@api_key_required
def get_quote(symbol):
    """Get latest quote for a stock"""
    data = MarketData.query.filter_by(symbol=symbol.upper()).order_by(MarketData.timestamp.desc()).first()
    if not data:
        return jsonify({'error': 'Symbol not found'}), 404
        
    return jsonify({
        'symbol': data.symbol,
        'price': float(data.price) if data.price else None,
        'change': float(data.change) if data.change else None,
        'changePercent': float(data.change_percent) if data.change_percent else None,
        'volume': data.volume,
        'timestamp': data.timestamp.isoformat() if data.timestamp else None
    })

@public_v1_bp.route('/crypto/quotes/<symbol>', methods=['GET'])
@api_key_required
def get_crypto_quote(symbol):
    """Get latest quote for a cryptocurrency"""
    data = CryptoMarketData.query.filter_by(symbol=symbol.upper()).order_by(CryptoMarketData.timestamp.desc()).first()
    if not data:
        return jsonify({'error': 'Symbol not found'}), 404
        
    return jsonify({
        'symbol': data.symbol,
        'price': float(data.price) if data.price else None,
        'change24h': float(data.change_24h) if data.change_24h else None,
        'volume24h': float(data.volume_24h) if data.volume_24h else None,
        'timestamp': data.timestamp.isoformat() if data.timestamp else None
    })

@public_v1_bp.route('/news/latest', methods=['GET'])
@api_key_required
def get_latest_news():
    """Get latest news articles"""
    news = NewsItem.query.order_by(NewsItem.published_at.desc()).limit(20).all()
    return jsonify([item.to_dict() for item in news])

@public_v1_bp.route('/education/courses', methods=['GET'])
@api_key_required
def get_courses():
    """Get available education courses"""
    courses = Course.query.filter_by(is_published=True).all()
    return jsonify([course.to_dict() for course in courses])

@public_v1_bp.route('/market/economic-events', methods=['GET'])
@api_key_required
def get_economic_events():
    """Get upcoming economic events"""
    events = EconomicEvent.query.filter(EconomicEvent.event_date >= datetime.utcnow()).order_by(EconomicEvent.event_date.asc()).limit(50).all()
    return jsonify([event.to_dict() for event in events])

@public_v1_bp.route('/media/tv-channels', methods=['GET'])
@api_key_required
def get_tv_channels():
    """Get active TV channels"""
    channels = TVChannel.query.filter_by(is_active=True).all()
    return jsonify([channel.to_dict() for channel in channels])

@public_v1_bp.route('/forex/rates', methods=['GET'])
@api_key_required
def get_forex_rates():
    """Get latest forex exchange rates"""
    rates = ForexRate.query.all()
    return jsonify([rate.to_dict() for rate in rates])

@public_v1_bp.route('/commodities/latest', methods=['GET'])
@api_key_required
def get_commodities():
    """Get latest commodity prices"""
    commodities = CommodityData.query.all()
    return jsonify([commodity.to_dict() for commodity in commodities])

@public_v1_bp.route('/sports/events', methods=['GET'])
@api_key_required
def get_sports_events():
    """Get live and upcoming sports events"""
    events = SportsEvent.query.filter_by(is_active=True).order_by(SportsEvent.event_date.desc()).limit(50).all()
    return jsonify([event.to_dict() for event in events])

