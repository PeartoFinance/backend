"""
Public Glossary API Routes
- Read-only access to financial glossary terms
"""
from flask import Blueprint, request, jsonify
from models import GlossaryTerm
from extensions import cache

glossary_bp = Blueprint('glossary', __name__)


@glossary_bp.route('/glossary', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_glossary_terms():
    """
    Get all published glossary terms.

    Optional query params:
      - category: filter by category (trading, investing, derivatives, banking, crypto, economics, technical)
      - search: search term/definition
      - country: country code filter
    """
    category = request.args.get('category')
    search = request.args.get('search', '').strip()
    header_country = request.headers.get('X-User-Country')

    query = GlossaryTerm.query

    if category:
        query = query.filter(GlossaryTerm.category == category)

    if search:
        search_term = f'%{search}%'
        query = query.filter(
            (GlossaryTerm.term.ilike(search_term)) |
            (GlossaryTerm.definition.ilike(search_term))
        )

    if header_country:
        hc = header_country.strip().upper()
        query = query.filter(
            (GlossaryTerm.country_code.in_([hc, 'GLOBAL'])) |
            (GlossaryTerm.country_code.is_(None))
        )

    terms = query.order_by(GlossaryTerm.term.asc()).all()

    # Build category list from results
    categories = sorted(list(set(t.category for t in terms if t.category)))

    return jsonify({
        'terms': [{
            'id': t.id,
            'term': t.term,
            'definition': t.definition,
            'category': t.category,
            'relatedTerms': t.related_terms,
        } for t in terms],
        'categories': categories,
        'total': len(terms),
    })


@glossary_bp.route('/glossary/<int:term_id>', methods=['GET'])
@cache.cached(timeout=300)
def get_glossary_term(term_id):
    """Get a single glossary term by ID"""
    term = GlossaryTerm.query.get_or_404(term_id)

    return jsonify({
        'id': term.id,
        'term': term.term,
        'definition': term.definition,
        'category': term.category,
        'relatedTerms': term.related_terms,
    })
