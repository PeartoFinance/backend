"""
Content API Routes
Endpoints for news, TV, radio, trending topics
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models.base import db
from models.media import TVChannel, RadioStation, TrendingTopic, ForexRate
from models.article import NewsItem

content_bp = Blueprint('content', __name__)


@content_bp.route('/news', methods=['GET'])
def get_news():
    """Get news items"""
    limit = min(int(request.args.get('limit', 10)), 50)
    category = request.args.get('category')
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        news_filter = (NewsItem.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        news_filter = (NewsItem.country_code == 'GLOBAL') if hc == 'GLOBAL' else (NewsItem.country_code == hc)

    query = NewsItem.query.filter(news_filter)
    if category:
        query = query.filter(NewsItem.category == category)

    items = query.order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    return jsonify([n.to_dict() for n in items])


@content_bp.route('/news/featured', methods=['GET'])
def get_featured_news():
    """Get featured news items"""
    limit = min(int(request.args.get('limit', 5)), 20)
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        news_filter = (NewsItem.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        news_filter = (NewsItem.country_code == 'GLOBAL') if hc == 'GLOBAL' else (NewsItem.country_code == hc)

    items = NewsItem.query.filter(news_filter).order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    return jsonify([n.to_dict() for n in items])


@content_bp.route('/tv', methods=['GET'])
def get_tv_channels():
    """Get TV channels"""
    limit = min(int(request.args.get('limit', 20)), 50)
    category = request.args.get('category')
    header_country = request.headers.get('X-User-Country')
    query = TVChannel.query.filter(TVChannel.is_active == True)
    if header_country is None:
        query = query.filter(TVChannel.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        if hc == 'GLOBAL':
            query = query.filter(TVChannel.country_code == 'GLOBAL')
        else:
            query = query.filter(TVChannel.country_code == hc)

    if category:
        query = query.filter(TVChannel.category == category)

    channels = query.order_by(TVChannel.sort_order).limit(limit).all()
    
    return jsonify([c.to_dict() for c in channels])


@content_bp.route('/radio', methods=['GET'])
def get_radio_stations():
    """Get radio stations"""
    limit = min(int(request.args.get('limit', 20)), 50)
    genre = request.args.get('genre')
    header_country = request.headers.get('X-User-Country')
    query = RadioStation.query.filter(RadioStation.is_active == True)
    if header_country is None:
        # prefer country_code field when present, fall back to 'country'
        if hasattr(RadioStation, 'country_code'):
            query = query.filter(RadioStation.country_code == 'US')
        else:
            # if model uses 'country' field
            query = query.filter(RadioStation.country == 'United States')
    else:
        hc = header_country.strip().upper()
        if hasattr(RadioStation, 'country_code'):
            if hc == 'GLOBAL':
                query = query.filter(RadioStation.country_code == 'GLOBAL')
            else:
                query = query.filter(RadioStation.country_code == hc)
        else:
            # try to match by country name for older models
            # Map common codes to names if necessary; default to leaving unfiltered
            if hc == 'US':
                query = query.filter(RadioStation.country == 'United States')

    if genre:
        query = query.filter(RadioStation.genre.ilike(f'%{genre}%'))

    stations = query.order_by(RadioStation.position).limit(limit).all()
    
    return jsonify([s.to_dict() for s in stations])


@content_bp.route('/trending', methods=['GET'])
def get_trending_topics():
    """Get trending topics"""
    limit = min(int(request.args.get('limit', 10)), 20)
    header_country = request.headers.get('X-User-Country')
    query = TrendingTopic.query
    if header_country is None:
        if hasattr(TrendingTopic, 'country_code'):
            query = query.filter(TrendingTopic.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        if hasattr(TrendingTopic, 'country_code'):
            query = query.filter(TrendingTopic.country_code == ('GLOBAL' if hc == 'GLOBAL' else hc))

    try:
        topics = query.order_by(TrendingTopic.rank).limit(limit).all()
        if topics:
            return jsonify([t.to_dict() for t in topics])
    except Exception:
        pass
    
    # Return default trending topics if no data
    return jsonify([
        {'id': 1, 'title': 'NVIDIA earnings beat expectations', 'category': 'Tech', 'rank': 1},
        {'id': 2, 'title': 'Bitcoin ETF approval speculation', 'category': 'Crypto', 'rank': 2},
        {'id': 3, 'title': 'Fed rate decision impact', 'category': 'Economy', 'rank': 3},
        {'id': 4, 'title': 'Tesla Cybertruck deliveries begin', 'category': 'Auto', 'rank': 4},
        {'id': 5, 'title': 'Oil prices surge on OPEC cuts', 'category': 'Energy', 'rank': 5},
    ])


@content_bp.route('/forex', methods=['GET'])
def get_forex_rates():
    """Get forex rates"""
    base = request.args.get('base', 'USD')
    
    try:
        rates = ForexRate.query.filter(ForexRate.base_currency == base).all()
        if rates:
            return jsonify([r.to_dict() for r in rates])
    except Exception:
        pass
    
    # Return default forex rates if no data
    return jsonify([
        {'pair': 'USD/EUR', 'rate': 0.9242, 'change': -0.0026, 'changePercent': -0.28, 'high': 0.9255, 'low': 0.9229},
        {'pair': 'USD/GBP', 'rate': 0.7935, 'change': -0.0073, 'changePercent': -0.92, 'high': 0.7872, 'low': 0.7888},
        {'pair': 'USD/JPY', 'rate': 149.85, 'change': -0.19, 'changePercent': -0.13, 'high': 149.95, 'low': 149.75},
        {'pair': 'USD/AUD', 'rate': 1.5187, 'change': 0.0126, 'changePercent': 0.83, 'high': 1.525, 'low': 1.5124},
        {'pair': 'USD/CAD', 'rate': 1.3654, 'change': 0.0016, 'changePercent': 0.12, 'high': 1.3662, 'low': 1.3646},
        {'pair': 'USD/CHF', 'rate': 0.8812, 'change': 0.0075, 'changePercent': 0.85, 'high': 0.8849, 'low': 0.8775},
    ])
