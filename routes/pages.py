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
    """
    country = request.args.get('country')
    status = request.args.get('status', 'published')

    query = Page.query
    if status:
        query = query.filter(Page.status == status)
    if country:
        query = query.filter(Page.country_code == country)

    pages = query.order_by(Page.created_at.desc()).all()

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
            'createdAt': p.created_at.isoformat() if p.created_at else None,
        } for p in pages]
    })


