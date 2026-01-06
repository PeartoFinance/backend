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
    
    # Try to get from news_items first (has summary, image_url)
    news = NewsItem.query.order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    if news:
        return jsonify([{
            'id': n.id,
            'title': n.title,
            'summary': n.summary,
            'author': n.source,
            'imageUrl': n.image_url,
            'category': n.category,
            'publishedAt': n.published_at.isoformat() if n.published_at else None,
        } for n in news])
    
    # Fallback to posts if exists
    posts = Post.query.filter(
        Post.is_featured == True,
        Post.status == 'published'
    ).order_by(desc(Post.published_at)).limit(limit).all()
    
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
    articles = Article.query.order_by(desc(Article.createdAt)).limit(limit).all()
    
    return jsonify([{
        'id': a.id,
        'title': a.title,
        'summary': a.metaDescription,
        'author': 'Staff Writer',
        'imageUrl': None,
        'category': a.category,
        'publishedAt': a.createdAt.isoformat() if a.createdAt else None,
    } for a in articles])


@articles_bp.route('/', methods=['GET'])
def get_articles():
    """Get articles with filters"""
    category = request.args.get('category')
    limit = min(int(request.args.get('limit', 10)), 50)
    
    # Use news items as primary source
    query = NewsItem.query
    if category:
        query = query.filter(NewsItem.category == category)
    
    items = query.order_by(desc(NewsItem.published_at)).limit(limit).all()
    
    return jsonify([{
        'id': n.id,
        'title': n.title,
        'summary': n.summary,
        'author': n.source,
        'imageUrl': n.image_url,
        'category': n.category,
        'publishedAt': n.published_at.isoformat() if n.published_at else None
    } for n in items])


@articles_bp.route('/<article_id>', methods=['GET'])
def get_article(article_id):
    """Get single article/news item by ID"""
    # Try news item first
    news = NewsItem.query.get(article_id)
    if news:
        return jsonify({
            'id': news.id,
            'title': news.title,
            'summary': news.summary,
            'content': news.summary,
            'author': news.source,
            'imageUrl': news.image_url,
            'category': news.category,
            'publishedAt': news.published_at.isoformat() if news.published_at else None,
            'url': news.url
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
