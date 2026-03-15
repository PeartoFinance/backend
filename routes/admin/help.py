"""
Admin Help Center Routes
CRUD for Help Categories and Articles
"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, HelpCategory, HelpArticle, AuditEvent
from ..decorators import admin_required, permission_required

help_bp = Blueprint('admin_help', __name__, url_prefix='/help')


def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=str(entity_id),
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


# ============================================================================
# HELP CATEGORIES
# ============================================================================

@help_bp.route('/categories', methods=['GET'])
@permission_required("help_center")
def get_categories():
    """List all help categories"""
    try:
        categories = HelpCategory.query.order_by(HelpCategory.order_index.asc()).all()

        return jsonify({
            'categories': [{
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'icon': c.icon,
                'description': c.description,
                'orderIndex': c.order_index,
                'isActive': c.is_active,
                'countryCode': c.country_code,
            } for c in categories],
            'total': len(categories)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@help_bp.route('/categories/<int:category_id>', methods=['GET'])
@permission_required("help_center")
def get_category(category_id):
    """Get single category"""
    try:
        c = HelpCategory.query.get_or_404(category_id)
        articles = HelpArticle.query.filter_by(category_id=category_id).count()

        return jsonify({
            'id': c.id,
            'name': c.name,
            'slug': c.slug,
            'icon': c.icon,
            'description': c.description,
            'orderIndex': c.order_index,
            'isActive': c.is_active,
            'countryCode': c.country_code,
            'articleCount': articles,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@help_bp.route('/categories', methods=['POST'])
@permission_required("help_center")
def create_category():
    """Create a help category"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400

        category = HelpCategory(
            name=data['name'],
            slug=data.get('slug', data['name'].lower().replace(' ', '-')),
            icon=data.get('icon'),
            description=data.get('description'),
            order_index=data.get('orderIndex', 0),
            is_active=data.get('isActive', True),
            country_code=data.get('countryCode', 'US')
        )

        db.session.add(category)
        db.session.commit()

        log_audit('HELP_CATEGORY_CREATE', 'help_category', category.id, {'name': data['name']})

        return jsonify({'ok': True, 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@help_bp.route('/categories/<int:category_id>', methods=['PUT'])
@permission_required("help_center")
def update_category(category_id):
    """Update a help category"""
    try:
        category = HelpCategory.query.get_or_404(category_id)
        data = request.get_json()

        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            category.slug = data['slug']
        if 'icon' in data:
            category.icon = data['icon']
        if 'description' in data:
            category.description = data['description']
        if 'orderIndex' in data:
            category.order_index = data['orderIndex']
        if 'isActive' in data:
            category.is_active = data['isActive']
        if 'countryCode' in data:
            category.country_code = data['countryCode']

        db.session.commit()
        log_audit('HELP_CATEGORY_UPDATE', 'help_category', category_id, data)

        return jsonify({'ok': True, 'message': 'Category updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@help_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@permission_required("help_center")
def delete_category(category_id):
    """Delete a help category"""
    try:
        category = HelpCategory.query.get_or_404(category_id)

        # Check for articles in this category
        articles = HelpArticle.query.filter_by(category_id=category_id).count()
        if articles > 0:
            return jsonify({'error': f'Cannot delete category with {articles} articles'}), 400

        db.session.delete(category)
        db.session.commit()

        log_audit('HELP_CATEGORY_DELETE', 'help_category', category_id)

        return jsonify({'ok': True, 'message': 'Category deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# HELP ARTICLES
# ============================================================================

@help_bp.route('/articles', methods=['GET'])
@permission_required("help_center")
def get_articles():
    """List all help articles"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category_id = request.args.get('category_id', type=int)
        search = request.args.get('search', '')
        is_featured = request.args.get('is_featured')

        query = HelpArticle.query

        if category_id:
            query = query.filter_by(category_id=category_id)
        if search:
            query = query.filter(
                (HelpArticle.title.ilike(f'%{search}%')) |
                (HelpArticle.content.ilike(f'%{search}%'))
            )
        if is_featured is not None:
            query = query.filter_by(is_featured=is_featured == 'true')

        articles = query.order_by(HelpArticle.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get categories
        cat_ids = list(set(a.category_id for a in articles.items if a.category_id))
        categories = {c.id: c for c in HelpCategory.query.filter(HelpCategory.id.in_(cat_ids)).all()}

        return jsonify({
            'articles': [{
                'id': a.id,
                'title': a.title,
                'slug': a.slug,
                'categoryId': a.category_id,
                'categoryName': categories.get(a.category_id).name if categories.get(a.category_id) else None,
                'isFeatured': a.is_featured,
                'viewCount': a.view_count,
                'helpfulCount': a.helpful_count,
                'isActive': a.is_active,
                'createdAt': a.created_at.isoformat() if a.created_at else None,
            } for a in articles.items],
            'total': articles.total,
            'pages': articles.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@help_bp.route('/articles/<int:article_id>', methods=['GET'])
@permission_required("help_center")
def get_article(article_id):
    """Get single article"""
    try:
        a = HelpArticle.query.get_or_404(article_id)
        category = HelpCategory.query.get(a.category_id) if a.category_id else None

        return jsonify({
            'id': a.id,
            'title': a.title,
            'slug': a.slug,
            'content': a.content,
            'categoryId': a.category_id,
            'categoryName': category.name if category else None,
            'isFeatured': a.is_featured,
            'viewCount': a.view_count,
            'helpfulCount': a.helpful_count,
            'isActive': a.is_active,
            'countryCode': a.country_code,
            'createdAt': a.created_at.isoformat() if a.created_at else None,
            'updatedAt': a.updated_at.isoformat() if a.updated_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@help_bp.route('/articles', methods=['POST'])
@permission_required("help_center")
def create_article():
    """Create a help article"""
    try:
        data = request.get_json()

        if not data.get('title'):
            return jsonify({'error': 'Article title is required'}), 400

        article = HelpArticle(
            title=data['title'],
            slug=data.get('slug', data['title'].lower().replace(' ', '-')),
            content=data.get('content', ''),
            category_id=data.get('categoryId'),
            is_featured=data.get('isFeatured', False),
            is_active=data.get('isActive', True),
            country_code=data.get('countryCode', 'US'),
            created_at=datetime.utcnow()
        )

        db.session.add(article)
        db.session.commit()

        log_audit('HELP_ARTICLE_CREATE', 'help_article', article.id, {'title': data['title']})

        return jsonify({'ok': True, 'id': article.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@help_bp.route('/articles/<int:article_id>', methods=['PUT'])
@permission_required("help_center")
def update_article(article_id):
    """Update a help article"""
    try:
        article = HelpArticle.query.get_or_404(article_id)
        data = request.get_json()

        if 'title' in data:
            article.title = data['title']
        if 'slug' in data:
            article.slug = data['slug']
        if 'content' in data:
            article.content = data['content']
        if 'categoryId' in data:
            article.category_id = data['categoryId']
        if 'isFeatured' in data:
            article.is_featured = data['isFeatured']
        if 'isActive' in data:
            article.is_active = data['isActive']
        if 'countryCode' in data:
            article.country_code = data['countryCode']

        db.session.commit()
        log_audit('HELP_ARTICLE_UPDATE', 'help_article', article_id, data)

        return jsonify({'ok': True, 'message': 'Article updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@help_bp.route('/articles/<int:article_id>', methods=['DELETE'])
@permission_required("help_center")
def delete_article(article_id):
    """Delete a help article"""
    try:
        article = HelpArticle.query.get_or_404(article_id)

        db.session.delete(article)
        db.session.commit()

        log_audit('HELP_ARTICLE_DELETE', 'help_article', article_id)

        return jsonify({'ok': True, 'message': 'Article deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# STATS
# ============================================================================

@help_bp.route('/stats', methods=['GET'])
@permission_required("help_center")
def get_help_stats():
    """Get help center statistics"""
    try:
        total_categories = HelpCategory.query.count()
        active_categories = HelpCategory.query.filter_by(is_active=True).count()
        total_articles = HelpArticle.query.count()
        active_articles = HelpArticle.query.filter_by(is_active=True).count()
        featured_articles = HelpArticle.query.filter_by(is_featured=True).count()

        return jsonify({
            'categories': {
                'total': total_categories,
                'active': active_categories,
            },
            'articles': {
                'total': total_articles,
                'active': active_articles,
                'featured': featured_articles,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
