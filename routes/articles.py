"""
Articles API Routes
Endpoints for articles and educational content
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models.base import db
from models.article import Article, NewsItem, Post

articles_bp = Blueprint('articles', __name__)


@articles_bp.route('/featured', methods=['GET'])
def get_featured_articles():
    """Get featured articles from news_items or posts"""
    limit = min(int(request.args.get('limit', 5)), 20)
    
    # Apply header-driven country scoping: no header -> US; header GLOBAL -> GLOBAL; else only header country
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        news_filter = (NewsItem.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        news_filter = (NewsItem.country_code == 'GLOBAL') if hc == 'GLOBAL' else (NewsItem.country_code == hc)

    # Try to get from news_items first (has summary, image_url)
    news = NewsItem.query.filter(news_filter).order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    if news:
        return jsonify([{
            'id': n.id,
            'title': n.title,
            'summary': n.summary,
            'author': n.source,
            'imageUrl': n.image,
            'category': n.category,
            'publishedAt': n.published_at.isoformat() if n.published_at else None,
        } for n in news])
    
    # Fallback to posts if exists
    posts_query = Post.query.filter(
        Post.is_featured == True,
        Post.status == 'published'
    )
    # if Post has country_code attribute, scope it; otherwise leave global
    if hasattr(Post, 'country_code'):
        if header_country is None:
            posts_query = posts_query.filter(Post.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            posts_query = posts_query.filter(Post.country_code == ('GLOBAL' if hc == 'GLOBAL' else hc))

    posts = posts_query.order_by(desc(Post.published_at)).limit(limit).all()
    
    if posts:
        return jsonify([{
            'id': p.id,
            'title': p.title,
            'summary': p.excerpt,
            'author': 'Staff Writer',
            'imageUrl': p.featured_image,
            'category': 'News',
            'publishedAt': p.published_at.isoformat() if p.published_at else None,
        } for p in posts])
    
    # Fallback to articles
    articles_query = Article.query
    if hasattr(Article, 'country_code'):
        if header_country is None:
            articles_query = articles_query.filter(Article.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            articles_query = articles_query.filter(Article.country_code == ('GLOBAL' if hc == 'GLOBAL' else hc))

    articles = articles_query.order_by(desc(Article.createdAt)).limit(limit).all()
    
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'summary': a.metaDescription,
        'author': 'Staff Writer',
        'imageUrl': None,
        'category': a.category,
        'publishedAt': a.createdAt.isoformat() if a.createdAt else None,
    } for a in articles])


@articles_bp.route('/categories', methods=['GET'])
def get_articles():
    """Get articles with filters"""
    category = request.args.get('category')
    limit = min(int(request.args.get('limit', 10)), 50)
    
    # Use news items as primary source with header-driven scoping
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
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'summary': n.summary,
        'author': n.source,
        'imageUrl': n.image,
        'category': n.category,
        'publishedAt': n.published_at.isoformat() if n.published_at else None
    } for n in items])


@articles_bp.route('/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get single article/news item by ID"""
    # Try news item first
    # For single article, respect header scoping: if header present and doesn't match, treat as not found
    news = NewsItem.query.get(article_id)
    if news:
        header_country = request.headers.get('X-User-Country')
        if header_country is None:
            if (news.country_code or 'US') != 'US':
                news = None
        else:
            hc = header_country.strip().upper()
            if hc == 'GLOBAL':
                if (news.country_code or '').upper() != 'GLOBAL':
                    news = None
            else:
                if (news.country_code or '').upper() != hc:
                    news = None

    if news:
        return jsonify({
            'id': news.id,
            'title': news.title,
            'summary': news.summary,
            'content': news.summary,
            'author': news.source,
            'imageUrl': news.image,
            'category': news.category,
            'publishedAt': news.published_at.isoformat() if news.published_at else None,
            'url': news.source_url
        })
    
    # Fallback to article
    article = Article.query.get(article_id)
    if article:
        return jsonify({
            'id': article.id,
            'title': article.title,
            'summary': article.metaDescription,
            'content': article.json,
            'author': 'Staff Writer',
            'imageUrl': None,
            'category': article.category,
            'publishedAt': article.createdAt.isoformat() if article.createdAt else None,
        })
    
    return jsonify({'error': 'Article not found'}), 404
