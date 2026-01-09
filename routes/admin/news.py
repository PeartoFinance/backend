"""
Admin News Management Routes
CRUD for /api/admin/news
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from .auth import admin_required
from models import db, NewsItem

news_bp = Blueprint('admin_news', __name__)


@news_bp.route('/news', methods=['GET'])
@admin_required
def get_news():
    """List all news articles"""
    try:
        articles = NewsItem.query.order_by(NewsItem.published_at.desc()).limit(500).all()
        return jsonify({
            'news': [a.to_dict() for a in articles]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['GET'])
@admin_required
def get_news_item(news_id):
    """Get single news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        return jsonify(article.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news', methods=['POST'])
@admin_required
def create_news():
    """Create news article"""
    try:
        data = request.get_json()
        article = NewsItem(
            title=data.get('title'),
            summary=data.get('summary'),
            source=data.get('source'),
            category=data.get('category'),
            image=data.get('image'),
            link=data.get('link'),
            slug=data.get('slug'),
            author=data.get('author'),
            full_content=data.get('full_content'),
            is_published=data.get('is_published', False),
            featured=data.get('featured', False),
            published_at=datetime.utcnow() if data.get('is_published') else None,
            created_at=datetime.utcnow()
        )
        db.session.add(article)
        db.session.commit()
        return jsonify({'ok': True, 'id': article.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['PUT'])
@admin_required
def update_news(news_id):
    """Update news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        data = request.get_json()
        
        if 'title' in data:
            article.title = data['title']
        if 'summary' in data:
            article.summary = data['summary']
        if 'source' in data:
            article.source = data['source']
        if 'category' in data:
            article.category = data['category']
        if 'image' in data:
            article.image = data['image']
        if 'link' in data:
            article.link = data['link']
        if 'slug' in data:
            article.slug = data['slug']
        if 'author' in data:
            article.author = data['author']
        if 'full_content' in data:
            article.full_content = data['full_content']
        if 'is_published' in data:
            article.is_published = data['is_published']
            if data['is_published'] and not article.published_at:
                article.published_at = datetime.utcnow()
        if 'featured' in data:
            article.featured = data['featured']
        
        article.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@news_bp.route('/news/<int:news_id>', methods=['DELETE'])
@admin_required
def delete_news(news_id):
    """Delete news article"""
    try:
        article = NewsItem.query.get_or_404(news_id)
        db.session.delete(article)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
