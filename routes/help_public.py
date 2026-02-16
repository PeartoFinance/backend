"""
Public Help Center API Routes
- Read-only access to help categories and articles
"""
from flask import Blueprint, request, jsonify
from models import HelpCategory, HelpArticle
from models.base import db
from extensions import cache

help_public_bp = Blueprint('help_public', __name__)


@help_public_bp.route('/help/categories', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_help_categories():
    """Get all active help categories with article counts"""
    header_country = request.headers.get('X-User-Country')

    query = HelpCategory.query.filter_by(is_active=True)

    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(
            (HelpCategory.country_code.in_([hc, 'GLOBAL'])) |
            (HelpCategory.country_code.is_(None))
        )

    categories = query.order_by(HelpCategory.order_index.asc()).all()

    result = []
    for c in categories:
        article_count = HelpArticle.query.filter_by(
            category_id=c.id, is_active=True
        ).count()
        result.append({
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'icon': c.icon,
            'description': c.description,
            'articleCount': article_count,
        })

    return jsonify({'categories': result, 'total': len(result)})


@help_public_bp.route('/help/categories/<slug>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_help_category_by_slug(slug):
    """Get a help category and its articles by slug"""
    category = HelpCategory.query.filter_by(slug=slug, is_active=True).first()
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    articles = HelpArticle.query.filter_by(
        category_id=category.id, is_active=True
    ).order_by(HelpArticle.created_at.desc()).all()

    return jsonify({
        'category': {
            'id': category.id,
            'name': category.name,
            'slug': category.slug,
            'icon': category.icon,
            'description': category.description,
        },
        'articles': [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'content': a.content,
            'isFeatured': a.is_featured,
            'viewCount': a.view_count,
            'helpfulCount': a.helpful_count,
            'createdAt': a.created_at.isoformat() if a.created_at else None,
        } for a in articles],
    })


@help_public_bp.route('/help/articles', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_help_articles():
    """Get help articles with optional filtering"""
    category_id = request.args.get('category_id', type=int)
    search = request.args.get('search', '').strip()
    featured = request.args.get('featured')
    header_country = request.headers.get('X-User-Country')

    query = HelpArticle.query.filter_by(is_active=True)

    if category_id:
        query = query.filter_by(category_id=category_id)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (HelpArticle.title.ilike(search_term)) |
            (HelpArticle.content.ilike(search_term))
        )

    if featured == 'true':
        query = query.filter_by(is_featured=True)

    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(
            (HelpArticle.country_code.in_([hc, 'GLOBAL'])) |
            (HelpArticle.country_code.is_(None))
        )

    articles = query.order_by(HelpArticle.created_at.desc()).all()

    # Get categories for each article
    cat_ids = list(set(a.category_id for a in articles if a.category_id))
    categories = {c.id: c for c in HelpCategory.query.filter(HelpCategory.id.in_(cat_ids)).all()} if cat_ids else {}

    return jsonify({
        'articles': [{
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'content': a.content,
            'categoryId': a.category_id,
            'categoryName': categories.get(a.category_id).name if categories.get(a.category_id) else None,
            'categorySlug': categories.get(a.category_id).slug if categories.get(a.category_id) else None,
            'isFeatured': a.is_featured,
            'viewCount': a.view_count,
            'helpfulCount': a.helpful_count,
            'createdAt': a.created_at.isoformat() if a.created_at else None,
        } for a in articles],
        'total': len(articles),
    })


@help_public_bp.route('/help/articles/<slug>', methods=['GET'])
def get_help_article_by_slug(slug):
    """Get a single help article by slug (increments view count)"""
    article = HelpArticle.query.filter_by(slug=slug, is_active=True).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    # Increment view count
    article.view_count = (article.view_count or 0) + 1
    db.session.commit()

    category = HelpCategory.query.get(article.category_id) if article.category_id else None

    return jsonify({
        'id': article.id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'categoryId': article.category_id,
        'categoryName': category.name if category else None,
        'categorySlug': category.slug if category else None,
        'isFeatured': article.is_featured,
        'viewCount': article.view_count,
        'helpfulCount': article.helpful_count,
        'createdAt': article.created_at.isoformat() if article.created_at else None,
        'updatedAt': article.updated_at.isoformat() if article.updated_at else None,
    })


@help_public_bp.route('/help/articles/<slug>/helpful', methods=['POST'])
def mark_article_helpful(slug):
    """Mark an article as helpful (increment helpful count)"""
    article = HelpArticle.query.filter_by(slug=slug, is_active=True).first()
    if not article:
        return jsonify({'error': 'Article not found'}), 404

    article.helpful_count = (article.helpful_count or 0) + 1
    db.session.commit()

    return jsonify({'ok': True, 'helpfulCount': article.helpful_count})
