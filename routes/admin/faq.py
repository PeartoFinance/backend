from flask import Blueprint, request, jsonify
from models import db, FAQ, AuditEvent
from datetime import datetime
import json, uuid
from ..decorators import admin_required

admin_faq_bp = Blueprint('admin_faq', __name__)

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

@admin_faq_bp.route('/content/faq', methods=['GET'])
@admin_required
def get_faqs():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status')
        
        query = FAQ.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (FAQ.question.ilike(search_term)) |
                (FAQ.answer.ilike(search_term)) |
                (FAQ.category.ilike(search_term))
            )
            
        if status == 'active':
            query = query.filter_by(active=True)
        elif status == 'inactive':
            query = query.filter_by(active=False)
            
        # Order by order_index asc, then created_at desc
        faqs = query.order_by(FAQ.order_index.asc(), FAQ.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'faqs': [{
                'id': f.id,
                'question': f.question,
                'answer': f.answer,
                'category': f.category,
                'orderIndex': f.order_index,
                'active': f.active,
                'showOnHomepage': f.show_on_homepage,
                'countryCode': f.country_code,
                'createdAt': f.created_at.isoformat()
            } for f in faqs.items],
            'total': faqs.total,
            'pages': faqs.pages,
            'currentPage': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_faq_bp.route('/content/faq', methods=['POST'])
@admin_required
def create_faq():
    try:
        data = request.get_json()
        
        if not data.get('question') or not data.get('answer'):
            return jsonify({'error': 'Question and Answer are required'}), 400
            
        faq_id = str(uuid.uuid4())
        
        faq = FAQ(
            id=faq_id,
            question=data['question'],
            answer=data['answer'],
            category=data.get('category', 'General'),
            order_index=data.get('orderIndex', 0),
            active=data.get('active', True),
            show_on_homepage=data.get('showOnHomepage', False),
            country_code=data.get('countryCode', 'GLOBAL'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(faq)
        db.session.commit()
        
        log_audit('FAQ_CREATE', 'faq', faq_id, {'question': data['question']})
        
        return jsonify({'ok': True, 'id': faq_id}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_faq_bp.route('/content/faq/<faq_id>', methods=['PUT'])
@admin_required
def update_faq(faq_id):
    try:
        faq = FAQ.query.get_or_404(faq_id)
        data = request.get_json()
        
        if 'question' in data:
            faq.question = data['question']
        if 'answer' in data:
            faq.answer = data['answer']
        if 'category' in data:
            faq.category = data['category']
        if 'orderIndex' in data:
            faq.order_index = data['orderIndex']
        if 'active' in data:
            faq.active = data['active']
        if 'showOnHomepage' in data:
            faq.show_on_homepage = data['showOnHomepage']
        if 'countryCode' in data:
            faq.country_code = data['countryCode']
            
        db.session.commit()
        
        log_audit('FAQ_UPDATE', 'faq', faq_id, data)
        
        return jsonify({'ok': True})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_faq_bp.route('/content/faq/<faq_id>', methods=['DELETE'])
@admin_required
def delete_faq(faq_id):
    """Soft delete FAQ"""
    try:
        faq = FAQ.query.get_or_404(faq_id)
        
        # Soft delete: just set active to False
        faq.active = False
        
        db.session.commit()
        log_audit('FAQ_DELETE_SOFT', 'faq', faq_id)
        
        return jsonify({'ok': True, 'message': 'FAQ soft deleted'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
