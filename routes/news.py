"""
News API Routes with SQLAlchemy
- Published news, single article, search, categories
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, or_
from models.article import NewsItem
from models.base import db

news_bp = Blueprint('news', __name__)


@news_bp.route('/published', methods=['GET'])
def get_published_news():
    """Get published news articles with country filtering"""
    limit = min(int(request.args.get('limit', 50)), 200)
    offset = int(request.args.get('offset', 0))
    category = request.args.get('category')
    country = getattr(request, 'user_country', 'US')
    
    query = NewsItem.query.filter(
        NewsItem.curated_status == 'published',
        or_(
            NewsItem.country_code == country,
            NewsItem.country_code == 'GLOBAL',
            NewsItem.country_code == None
        )
    )
    
    if category:
        query = query.filter(NewsItem.category == category)
    
    # Order: prioritize country match, then featured, then items with images, then date
    articles = query.order_by(
        desc(NewsItem.country_code == country),
        desc(NewsItem.featured),
        desc(NewsItem.image != None),
        desc(NewsItem.published_at)
    ).offset(offset).limit(limit).all()
    
    return jsonify({
        'items': [a.to_dict() for a in articles],
        'total': len(articles),
        'limit': limit,
        'offset': offset,
        'source': 'database'
    })


@news_bp.route('/headlines', methods=['GET'])
def get_headlines():
    """Get latest news headlines with country filtering"""
    limit = min(int(request.args.get('limit', 20)), 100)
    page = max(int(request.args.get('page', 1)), 1)
    category = request.args.get('category')
    country = getattr(request, 'user_country', 'US')
    
    offset = (page - 1) * limit
    
    query = NewsItem.query.filter(
        NewsItem.curated_status == 'published',
        or_(
            NewsItem.country_code == country,
            NewsItem.country_code == 'GLOBAL',
            NewsItem.country_code == None
        )
    )
    
    if category:
        query = query.filter(NewsItem.category == category)
    
    articles = query.order_by(
        desc(NewsItem.featured),
        desc(NewsItem.published_at)
    ).offset(offset).limit(limit).all()
    
    return jsonify({
        'articles': [a.to_dict() for a in articles],
        'page': page,
        'limit': limit
    })


@news_bp.route('/search', methods=['GET'])
def search_news():
    """Search news articles"""
    query_str = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    country = getattr(request, 'user_country', 'US')
    
    if not query_str or len(query_str) < 2:
        return jsonify({'error': 'q parameter required (min 2 chars)'}), 400
    
    articles = NewsItem.query.filter(
        NewsItem.curated_status == 'published',
        or_(
            NewsItem.country_code == country,
            NewsItem.country_code == 'GLOBAL',
            NewsItem.country_code == None
        ),
        or_(
            NewsItem.title.ilike(f'%{query_str}%'),
            NewsItem.summary.ilike(f'%{query_str}%')
        )
    ).order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    return jsonify({
        'q': query_str,
        'items': [a.to_dict() for a in articles],
        'total': len(articles)
    })


@news_bp.route('/featured', methods=['GET'])
def get_featured():
    """Get featured news articles"""
    limit = min(int(request.args.get('limit', 5)), 20)
    country = getattr(request, 'user_country', 'US')
    
    articles = NewsItem.query.filter(
        NewsItem.curated_status == 'published',
        NewsItem.featured == True,
        or_(
            NewsItem.country_code == country,
            NewsItem.country_code == 'GLOBAL',
            NewsItem.country_code == None
        )
    ).order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    return jsonify([a.to_dict() for a in articles])


@news_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get available news categories"""
    categories = db.session.query(NewsItem.category).filter(
        NewsItem.curated_status == 'published',
        NewsItem.category != None
    ).distinct().all()
    
    return jsonify([c[0] for c in categories if c[0]])


@news_bp.route('/article/<slug>', methods=['GET'])
def get_article_by_slug(slug):
    """Get single article by slug"""
    if not slug or len(slug) < 1:
        return jsonify({'success': False, 'error': 'Invalid slug'}), 400
    
    article = NewsItem.query.filter(
        NewsItem.slug == slug,
        NewsItem.curated_status == 'published'
    ).first()
    
    if not article:
        return jsonify({'success': False, 'error': 'Article not found'}), 404
    
    return jsonify({
        'success': True,
        'data': {
            'id': article.id,
            'title': article.title,
            'summary': article.summary,
            'full_content': article.full_content or article.summary or '',
            'author': article.author or 'Pearto Team',
            'image': article.image,
            'category': article.category or 'general',
            'source': article.source,
            'source_type': article.source_type or 'admin',
            'slug': article.slug,
            'canonical_url': article.canonical_url,
            'published_at': article.published_at.isoformat() if article.published_at else None,
            'meta_description': article.meta_description or article.summary or '',
            'country_code': article.country_code
        }
    })


@news_bp.route('/article/id/<int:article_id>', methods=['GET'])
def get_article_by_id(article_id):
    """Get single article by ID"""
    article = NewsItem.query.get(article_id)
    
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    return jsonify({
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.summary,
        'content': article.full_content,
        'url': article.canonical_url,
        'image': article.image,
        'source': article.source,
        'category': article.category,
        'featured': article.featured,
        'publishedAt': article.published_at.isoformat() if article.published_at else None
    })
