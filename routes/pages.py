"""
Public Pages API Routes
- Read-only access to CMS pages
"""
from flask import Blueprint, request, jsonify
from models import Page


pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/pages', methods=['GET'])
def get_pages():
    """
    Public pages listing.

    Optional query params:
      - country: filter by country_code
      - status: default 'published'
      - placement: filter by placement (header, sidebar, footer, resources)
    """
    country = request.args.get('country')
    status = request.args.get('status', 'published')
    placement = request.args.get('placement')

    # header-driven country scoping: header overrides query param
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = Page.country_code.in_([hc, 'GLOBAL'])
    elif country:
        # if explicit query param provided use it
        country_filter = Page.country_code.in_([country.strip().upper(), 'GLOBAL'])
    else:
        # no header or query param -> include all pages (for API flexibility)
        country_filter = True

    query = Page.query
    if status:
        query = query.filter(Page.status == status)
    if country_filter is not True:
        query = query.filter(country_filter)
    
    # Filter by placement if specified
    if placement:
        query = query.filter(Page.placement.contains(placement))

    pages = query.order_by(Page.sort_order.asc(), Page.created_at.desc()).all()

    return jsonify({
        'pages': [{
            'id': p.id,
            'title': p.title,
            'slug': p.slug,
            'content': p.content,
            'metaTitle': p.meta_title,
            'metaDescription': p.meta_description,
            'template': p.template,
            'status': p.status,
            'isHomepage': p.is_homepage,
            'countryCode': p.country_code,
            'placement': p.placement,
            'featuredImage': p.featured_image,
            'sortOrder': p.sort_order,
            'createdAt': p.created_at.isoformat() if p.created_at else None,
        } for p in pages]
    })


@pages_bp.route('/pages/<slug>', methods=['GET'])
def get_page_by_slug(slug):
    """Get a single page by slug"""
    page = Page.query.filter_by(slug=slug, status='published').first()
    
    if not page:
        return jsonify({'error': 'Page not found'}), 404
    
    return jsonify({
        'page': {
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'content': page.content,
            'metaTitle': page.meta_title,
            'metaDescription': page.meta_description,
            'template': page.template,
            'status': page.status,
            'isHomepage': page.is_homepage,
            'countryCode': page.country_code,
            'placement': page.placement,
            'featuredImage': page.featured_image,
            'createdAt': page.created_at.isoformat() if page.created_at else None,
        }
    })

