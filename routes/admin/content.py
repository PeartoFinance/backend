"""
Admin Content Management Routes
CRUD for pages, posts, categories
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from .auth import admin_required
from models import db, Page, Post, PostCategory

content_bp = Blueprint('admin_content', __name__)


# ============ PAGES ============

@content_bp.route('/pages', methods=['GET'])
@admin_required
def get_pages():
    """List all pages"""
    try:
        pages = Page.query.order_by(Page.created_at.desc()).all()
        return jsonify({
            'pages': [{
                'id': p.id,
                'title': p.title,
                'slug': p.slug,
                'content': p.content,
                'is_published': p.is_published,
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
            title=data.get('title'),
            slug=data.get('slug'),
            content=data.get('content'),
            is_published=data.get('is_published', False),
            created_at=datetime.utcnow()
        )
        db.session.add(page)
        db.session.commit()
        return jsonify({'ok': True, 'id': page.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages/<int:page_id>', methods=['PUT'])
@admin_required
def update_page(page_id):
    """Update page"""
    try:
        page = Page.query.get_or_404(page_id)
        data = request.get_json()
        
        if 'title' in data:
            page.title = data['title']
        if 'slug' in data:
            page.slug = data['slug']
        if 'content' in data:
            page.content = data['content']
        if 'is_published' in data:
            page.is_published = data['is_published']
        
        page.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/pages/<int:page_id>', methods=['DELETE'])
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
        posts = Post.query.order_by(Post.created_at.desc()).limit(500).all()
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
            title=data.get('title'),
            slug=data.get('slug'),
            content=data.get('content'),
            excerpt=data.get('excerpt'),
            status=data.get('status', 'draft'),
            featured_image=data.get('featured_image'),
            created_at=datetime.utcnow()
        )
        db.session.add(post)
        db.session.commit()
        return jsonify({'ok': True, 'id': post.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/posts/<int:post_id>', methods=['PUT'])
@admin_required
def update_post(post_id):
    """Update post"""
    try:
        post = Post.query.get_or_404(post_id)
        data = request.get_json()
        
        for field in ['title', 'slug', 'content', 'excerpt', 'status', 'featured_image']:
            if field in data:
                setattr(post, field, data[field])
        
        post.updated_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@content_bp.route('/posts/<int:post_id>', methods=['DELETE'])
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
