"""
Content API Routes
Endpoints for news, TV, radio, trending topics
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models.base import db
from models.media import TVChannel, RadioStation, TrendingTopic, ForexRate
from models.article import NewsItem
from models.misc import Testimonial, FAQ, TeamMember
from extensions import cache

content_bp = Blueprint('content', __name__)


@content_bp.route('/news', methods=['GET'])
def get_news():
    """Get news items"""
    limit = min(int(request.args.get('limit', 10)), 50)
    category = request.args.get('category')
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        news_filter = NewsItem.country_code.in_([hc, 'GLOBAL'])
    else:
        news_filter = (NewsItem.country_code == 'GLOBAL')

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
@cache.cached(timeout=120, query_string=True)
def get_tv_channels():
    """Get TV channels"""
    limit = min(int(request.args.get('limit', 20)), 50)
    category = request.args.get('category')
    header_country = request.headers.get('X-User-Country')
    query = TVChannel.query.filter(TVChannel.is_active == True)
    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(TVChannel.country_code.in_([hc, 'GLOBAL']))
    else:
        query = query.filter(TVChannel.country_code == 'GLOBAL')

    if category:
        query = query.filter(TVChannel.category == category)

    channels = query.order_by(TVChannel.sort_order).limit(limit).all()
    
    return jsonify([c.to_dict() for c in channels])


@content_bp.route('/radio', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_radio_stations():
    """Get radio stations"""
    limit = min(int(request.args.get('limit', 20)), 50)
    genre = request.args.get('genre')
    header_country = request.headers.get('X-User-Country')
    query = RadioStation.query.filter(RadioStation.is_active == True)
    if header_country:
        hc = header_country.strip().upper()
        if hasattr(RadioStation, 'country_code'):
            query = query.filter(RadioStation.country_code.in_([hc, 'GLOBAL']))
        else:
            if hc == 'US':
                query = query.filter(RadioStation.country == 'United States')
    else:
        if hasattr(RadioStation, 'country_code'):
            query = query.filter(RadioStation.country_code == 'GLOBAL')

    if genre:
        query = query.filter(RadioStation.genre.ilike(f'%{genre}%'))

    stations = query.order_by(RadioStation.position).limit(limit).all()
    
    return jsonify([s.to_dict() for s in stations])


@content_bp.route('/trending', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_trending_topics():
    """Get trending topics"""
    limit = min(int(request.args.get('limit', 10)), 20)
    header_country = request.headers.get('X-User-Country')
    query = TrendingTopic.query
    if header_country:
        hc = header_country.strip().upper()
        if hasattr(TrendingTopic, 'country_code'):
            query = query.filter(TrendingTopic.country_code.in_([hc, 'GLOBAL']))
    else:
        if hasattr(TrendingTopic, 'country_code'):
            query = query.filter(TrendingTopic.country_code == 'GLOBAL')

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


@content_bp.route('/testimonials', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_testimonials():
    """Get active testimonials"""
    limit = min(int(request.args.get('limit', 10)), 50)
    featured = request.args.get('featured')
    header_country = request.headers.get('X-User-Country')
    
    query = Testimonial.query.filter(Testimonial.is_active == True)
    
    if featured == 'true':
        query = query.filter(Testimonial.is_featured == True)
        
    if header_country:
        hc = header_country.strip().upper()
        # Filter by specific country or global, similar to other content
        query = query.filter(Testimonial.country_code.in_([hc, 'GLOBAL']))
    
    # Order by featured first, then newest
    testimonials = query.order_by(
        desc(Testimonial.is_featured),
        desc(Testimonial.created_at)
    ).limit(limit).all()
        
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'title': t.title,
        'company': t.company,
        'avatarUrl': t.avatar_url,
        'content': t.content,
        'rating': t.rating,
        'countryCode': t.country_code,
        'createdAt': t.created_at.isoformat()
    } for t in testimonials])

@content_bp.route('/faq', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_faqs():
    """Get active FAQs"""
    # limit = min(int(request.args.get('limit', 50)), 100) # Typically show all or many
    category = request.args.get('category')
    homepage = request.args.get('homepage')
    header_country = request.headers.get('X-User-Country')
    
    query = FAQ.query.filter(FAQ.active == True)
    
    if category:
        query = query.filter(FAQ.category == category)
        
    if homepage == 'true':
        query = query.filter(FAQ.show_on_homepage == True)
        
    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(FAQ.country_code.in_([hc, 'GLOBAL']))
    
    # Order by order_index asc, then created_at desc
    faqs = query.order_by(FAQ.order_index.asc(), FAQ.created_at.desc()).all()
        
    return jsonify([{
        'id': f.id,
        'question': f.question,
        'answer': f.answer,
        'category': f.category,
        'active': f.active,
        'orderIndex': f.order_index,
        'countryCode': f.country_code
    } for f in faqs])


@content_bp.route('/teams', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_teams():
    """Get active team members"""
    limit = min(int(request.args.get('limit', 50)), 100)
    header_country = request.headers.get('X-User-Country')
    
    query = TeamMember.query.filter(TeamMember.is_active == True)
        
    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(TeamMember.country_code.in_([hc, 'GLOBAL']))
    else:
        query = query.filter(TeamMember.country_code == 'GLOBAL')
    
    # Order by sort_order asc, then created_at desc
    members = query.order_by(TeamMember.sort_order.asc(), TeamMember.created_at.desc()).limit(limit).all()
        
    return jsonify([m.to_dict() for m in members])


@content_bp.route('/teams/<int:member_id>', methods=['GET'])
@cache.cached(timeout=300)
def get_team_member(member_id):
    """Get single active team member detail"""
    member = TeamMember.query.filter_by(id=member_id, is_active=True).first_or_404()
    return jsonify(member.to_dict())
