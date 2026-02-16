"""
Admin Glossary CRUD Routes
Manage glossary terms from the admin panel
"""
from flask import Blueprint, request, jsonify
from models import db, GlossaryTerm, AuditEvent
from datetime import datetime
import json, uuid
from ..decorators import admin_required

admin_glossary_bp = Blueprint('admin_glossary', __name__)

def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=entity_id,
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


@admin_glossary_bp.route('/content/glossary', methods=['GET'])
@admin_required
def get_glossary_terms():
    """List all glossary terms with pagination, search and category filter"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', '')

        query = GlossaryTerm.query

        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (GlossaryTerm.term.ilike(search_term)) |
                (GlossaryTerm.definition.ilike(search_term))
            )

        if category:
            query = query.filter_by(category=category)

        terms = query.order_by(GlossaryTerm.term.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'terms': [t.to_dict() for t in terms.items],
            'total': terms.total,
            'pages': terms.pages,
            'currentPage': page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_glossary_bp.route('/content/glossary', methods=['POST'])
@admin_required
def create_glossary_term():
    """Create a new glossary term"""
    try:
        data = request.get_json()

        if not data.get('term') or not data.get('definition'):
            return jsonify({'error': 'Term and definition are required'}), 400

        # Check duplicate
        existing = GlossaryTerm.query.filter(
            GlossaryTerm.term.ilike(data['term'])
        ).first()
        if existing:
            return jsonify({'error': 'A term with this name already exists'}), 409

        term = GlossaryTerm(
            term=data['term'],
            definition=data['definition'],
            category=data.get('category', 'trading'),
            related_terms=data.get('relatedTerms'),
            country_code=data.get('countryCode', 'GLOBAL'),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(term)
        db.session.commit()

        log_audit('GLOSSARY_CREATE', 'glossary_term', str(term.id), {'term': data['term']})

        return jsonify({'ok': True, 'id': term.id, 'term': term.to_dict()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_glossary_bp.route('/content/glossary/<int:term_id>', methods=['PUT'])
@admin_required
def update_glossary_term(term_id):
    """Update an existing glossary term"""
    try:
        term = GlossaryTerm.query.get_or_404(term_id)
        data = request.get_json()

        if 'term' in data:
            term.term = data['term']
        if 'definition' in data:
            term.definition = data['definition']
        if 'category' in data:
            term.category = data['category']
        if 'relatedTerms' in data:
            term.related_terms = data['relatedTerms']
        if 'countryCode' in data:
            term.country_code = data['countryCode']

        term.updated_at = datetime.utcnow()
        db.session.commit()

        log_audit('GLOSSARY_UPDATE', 'glossary_term', str(term_id), data)

        return jsonify({'ok': True, 'term': term.to_dict()})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_glossary_bp.route('/content/glossary/<int:term_id>', methods=['DELETE'])
@admin_required
def delete_glossary_term(term_id):
    """Delete a glossary term"""
    try:
        term = GlossaryTerm.query.get_or_404(term_id)

        db.session.delete(term)
        db.session.commit()

        log_audit('GLOSSARY_DELETE', 'glossary_term', str(term_id), {'term': term.term})

        return jsonify({'ok': True, 'message': 'Term deleted'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
