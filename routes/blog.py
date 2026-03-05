"""
Blog API Routes
- Published posts, single post by slug, search, categories
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, or_
from models.article import Post, PostCategory
from models.base import db
from extensions import cache
from utils.validators import safe_pagination

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/published', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_published_posts():
    """Get published blog posts with pagination, category & search filtering"""
    limit, offset = safe_pagination(
        request.args.get('limit'),
        request.args.get('offset'),
        max_limit=200,
        max_offset=10000
    )
    category = request.args.get('category')
    search = request.args.get('search')
    country = getattr(request, 'user_country', None)

    query = Post.query.filter(Post.status == 'published')

    # Country filtering
    if country:
        query = query.filter(
            or_(
                Post.country_code == country,
                Post.country_code == 'GLOBAL',
                Post.country_code == None
            )
        )

    # Category filtering by slug
    if category:
        cat = PostCategory.query.filter_by(slug=category, is_active=True).first()
        if cat:
            query = query.filter(Post.category_id == cat.id)

    # Search filtering
    if search:
        keywords = [k.strip() for k in search.split() if k.strip()]
        if keywords:
            keyword_filters = []
            for kw in keywords:
                term = f'%{kw}%'
                keyword_filters.append(Post.title.ilike(term))
                keyword_filters.append(Post.excerpt.ilike(term))
            query = query.filter(or_(*keyword_filters))

    total_count = query.count()

    posts = query.order_by(
        desc(Post.is_featured),
        desc(Post.published_at)
    ).offset(offset).limit(limit).all()

    return jsonify({
        'items': [p.to_public_dict() for p in posts],
        'total': total_count,
        'limit': limit,
        'offset': offset
    })


@blog_bp.route('/categories', methods=['GET'])
@cache.cached(timeout=300)
def get_blog_categories():
    """Return active blog categories with published post counts"""
    from sqlalchemy import func

    rows = db.session.query(
        PostCategory.id,
        PostCategory.name,
        PostCategory.slug,
        PostCategory.icon,
        PostCategory.color,
        func.count(Post.id).label('count')
    ).outerjoin(Post, (Post.category_id == PostCategory.id) & (Post.status == 'published'))\
     .filter(PostCategory.is_active == True)\
     .group_by(PostCategory.id)\
     .order_by(PostCategory.sort_order, PostCategory.name)\
     .all()

    categories = [{
        'id': r.id,
        'name': r.name,
        'slug': r.slug,
        'icon': r.icon,
        'color': r.color,
        'count': r.count
    } for r in rows]

    return jsonify({'categories': categories})


@blog_bp.route('/<slug>', methods=['GET'])
def get_post_by_slug(slug):
    """Get a single published blog post by slug and increment view count"""
    post = Post.query.filter_by(slug=slug, status='published').first()
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Increment view count
    post.view_count = (post.view_count or 0) + 1
    db.session.commit()

    data = post.to_public_dict()
    data['content'] = post.content

    # Attach category info
    if post.category_id:
        cat = PostCategory.query.get(post.category_id)
        if cat:
            data['category'] = {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'icon': cat.icon,
                'color': cat.color
            }

    return jsonify(data)


@blog_bp.route('/featured', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_featured_posts():
    """Get featured blog posts"""
    limit = min(int(request.args.get('limit', 5)), 20)

    posts = Post.query.filter(
        Post.status == 'published',
        Post.is_featured == True
    ).order_by(desc(Post.published_at)).limit(limit).all()

    return jsonify([p.to_public_dict() for p in posts])
