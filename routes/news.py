"""
News API Routes with SQLAlchemy
- Headlines, search, categories
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, or_
from models.db import db, Article

news_bp = Blueprint('news', __name__)


@news_bp.route('/headlines', methods=['GET'])
def get_headlines():
    """Get latest news headlines with country filtering"""
    limit = min(int(request.args.get('limit', 20)), 100)
    page = max(int(request.args.get('page', 1)), 1)
    category = request.args.get('category')
    country = request.user_country
    
    offset = (page - 1) * limit
    
    query = Article.query.filter(
        Article.curated_status == 'published',
        or_(
            Article.country_code == country,
            Article.country_code == 'GLOBAL',
            Article.country_code == None
        )
    )
    
    if category:
        query = query.filter(Article.category == category)
    
    # Order by country match first (prioritize user's country), then by date
    articles = query.order_by(
        desc(Article.featured),
        desc(Article.published_at)
    ).offset(offset).limit(limit).all()
    
    return jsonify({
        'articles': [a.to_dict() for a in articles],
        'page': page,
        'limit': limit
    })


@news_bp.route('/search', methods=['GET'])
def search_news():
    """Search news articles"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    country = request.user_country
    
    if not query:
        return jsonify({'error': 'q parameter required'}), 400
    
    articles = Article.query.filter(
        Article.curated_status == 'published',
        or_(
            Article.country_code == country,
            Article.country_code == 'GLOBAL',
            Article.country_code == None
        ),
        or_(
            Article.title.ilike(f'%{query}%'),
            Article.summary.ilike(f'%{query}%')
        )
    ).order_by(desc(Article.published_at)).limit(limit).all()
    
    return jsonify([a.to_dict() for a in articles])


@news_bp.route('/featured', methods=['GET'])
def get_featured():
    """Get featured news articles"""
    limit = min(int(request.args.get('limit', 5)), 20)
    country = request.user_country
    
    articles = Article.query.filter(
        Article.curated_status == 'published',
        Article.featured == True,
        or_(
            Article.country_code == country,
            Article.country_code == 'GLOBAL',
            Article.country_code == None
        )
    ).order_by(desc(Article.published_at)).limit(limit).all()
    
    return jsonify([a.to_dict() for a in articles])


@news_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get available news categories"""
    categories = db.session.query(Article.category).filter(
        Article.curated_status == 'published',
        Article.category != None
    ).distinct().all()
    
    return jsonify([c[0] for c in categories if c[0]])


@news_bp.route('/article/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get single article by ID"""
    article = Article.query.get(article_id)
    
    if not article:
        return jsonify({'error': 'Article not found'}), 404
    
    return jsonify({
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'summary': article.summary,
        'content': article.content,
        'url': article.canonical_url,
        'image': article.image,
        'source': article.source,
        'category': article.category,
        'featured': article.featured,
        'publishedAt': article.published_at.isoformat() if article.published_at else None
    })
