"""
Admin Content Management Routes
CRUD for pages, posts, categories
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
import uuid
from ..decorators import admin_required
from models import db, Page, Post, PostCategory

content_bp = Blueprint('admin_content', __name__)


# ============ PAGES ============

@content_bp.route('/pages', methods=['GET'])
@admin_required
def get_pages():
    """List all pages"""
    try:
        country = getattr(request, 'user_country', 'US')
        pages = Page.query.filter(
            (Page.country_code == country) | 
            (Page.country_code == 'GLOBAL') |
            (Page.country_code == None)
        ).order_by(Page.sort_order.asc(), Page.created_at.desc()).all()
        return jsonify({
            'pages': [{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'content': p.content,
                'meta_title': p.meta_title,
                'meta_description': p.meta_description,
                'template': p.template,
                'status': p.status,
                'placement': p.placement,
                'featured_image': p.featured_image,
                'sort_order': p.sort_order,
                'country_code': p.country_code,
                'created_at': p.created_at.isoformat() if p.created_at else None,
            } for p in pages]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages', methods=['POST'])
@admin_required
def create_page():
    """Create page"""
    try:
        data = request.get_json()
        page = Page(
            id=str(uuid.uuid4()),
            title=data.get('title'),
            slug=data.get('slug'),
            content=data.get('content'),
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description'),
            template=data.get('template', 'default'),
            status=data.get('status', 'draft'),
            placement=data.get('placement', 'none'),
            featured_image=data.get('featured_image'),
            sort_order=data.get('sort_order', 0),
            created_at=datetime.utcnow(),
            country_code=data.get('country_code', getattr(request, 'user_country', 'GLOBAL'))
        )
        db.session.add(page)
        db.session.commit()
        return jsonify({'ok': True, 'id': page.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages/<page_id>', methods=['GET'])
@admin_required
def get_page(page_id):
    """Get single page"""
    try:
        page = Page.query.get_or_404(page_id)
        return jsonify({
            'page': {
                'id': page.id,
                'title': page.title,
                'slug': page.slug,
                'content': page.content,
                'meta_title': page.meta_title,
                'meta_description': page.meta_description,
                'template': page.template,
                'status': page.status,
                'placement': page.placement,
                'featured_image': page.featured_image,
                'sort_order': page.sort_order,
                'country_code': page.country_code,
                'created_at': page.created_at.isoformat() if page.created_at else None,
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages/<page_id>', methods=['PUT'])
@admin_required
def update_page(page_id):
    """Update page"""
    try:
        page = Page.query.get_or_404(page_id)
        data = request.get_json()
        
        for field in ['title', 'slug', 'content', 'meta_title', 'meta_description', 
                      'template', 'status', 'placement', 'featured_image', 
                      'sort_order', 'country_code']:
            if field in data:
                setattr(page, field, data[field])
        
        page.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages/<page_id>', methods=['DELETE'])
@admin_required
def delete_page(page_id):
    """Delete page"""
    try:
        page = Page.query.get_or_404(page_id)
        db.session.delete(page)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ POSTS ============

@content_bp.route('/posts', methods=['GET'])
@admin_required
def get_posts():
    """List all posts"""
    try:
        country = getattr(request, 'user_country', 'US')
        posts = Post.query.filter(
            (Post.country_code == country) | 
            (Post.country_code == 'GLOBAL')
        ).order_by(Post.created_at.desc()).limit(500).all()
        return jsonify({
            'posts': [{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'excerpt': p.excerpt,
                'status': p.status,
                'featured_image': p.featured_image,
                'created_at': p.created_at.isoformat() if p.created_at else None,
            } for p in posts]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_bp.route('/posts', methods=['POST'])
@admin_required
def create_post():
    """Create post"""
    try:
        data = request.get_json()
        post = Post(
            id=str(uuid.uuid4()),
            title=data.get('title'),
            slug=data.get('slug'),
            content=data.get('content'),
            excerpt=data.get('excerpt'),
            status=data.get('status', 'draft'),
            featured_image=data.get('featured_image'),
            category_id=data.get('category_id'),
            is_featured=data.get('is_featured', False),
            tags=data.get('tags'),
            meta_title=data.get('meta_title'),
            meta_description=data.get('meta_description'),
            published_at=datetime.utcnow() if data.get('status') == 'published' else None,
            created_at=datetime.utcnow(),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'ok': True, 'id': post.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/posts/<post_id>', methods=['PUT'])
@admin_required
def update_post(post_id):
    """Update post"""
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()
        
        for field in ['title', 'slug', 'content', 'excerpt', 'status', 'featured_image',
                     'country_code', 'category_id', 'is_featured', 'tags', 'meta_title', 'meta_description']:
            if field in data:
                setattr(post, field, data[field])
        
        # Set published_at when first published
        if data.get('status') == 'published' and not post.published_at:
            post.published_at = datetime.utcnow()
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/posts/<post_id>', methods=['DELETE'])
@admin_required
def delete_post(post_id):
    """Delete post"""
    try:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ CATEGORIES ============

@content_bp.route('/categories', methods=['GET'])
@admin_required
def get_categories():
    """List all categories"""
    try:
        categories = PostCategory.query.all()
        return jsonify({
            'categories': [{
                'id': c.id,
                'name': c.name,
                'slug': c.slug,
                'description': c.description,
            } for c in categories]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@content_bp.route('/categories', methods=['POST'])
@admin_required
def create_category():
    """Create category"""
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'error': 'Category name is required'}), 400

        category = PostCategory(
            name=data['name'],
            slug=data.get('slug', data['name'].lower().replace(' ', '-')),
            description=data.get('description', '')
        )
        db.session.add(category)
        db.session.commit()
        return jsonify({'ok': True, 'id': category.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """Update category"""
    try:
        category = PostCategory.query.get_or_404(category_id)
        data = request.get_json()

        if 'name' in data:
            category.name = data['name']
        if 'slug' in data:
            category.slug = data['slug']
        if 'description' in data:
            category.description = data['description']

        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """Delete category"""
    try:
        category = PostCategory.query.get_or_404(category_id)
        db.session.delete(category)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
