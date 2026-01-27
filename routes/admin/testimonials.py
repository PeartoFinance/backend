from flask import Blueprint, request, jsonify
from models import db, Testimonial, AuditEvent
from datetime import datetime
import json, uuid
from ..decorators import admin_required

admin_testimonials_bp = Blueprint('admin_testimonials', __name__)

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

@admin_testimonials_bp.route('/content/testimonials', methods=['GET'])
@admin_required
def get_testimonials():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status = request.args.get('status')  # active, inactive, all
        
        query = Testimonial.query
        
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Testimonial.name.ilike(search_term)) |
                (Testimonial.company.ilike(search_term)) |
                (Testimonial.content.ilike(search_term))
            )
            
        if status == 'active':
            query = query.filter_by(is_active=True)
        elif status == 'inactive':
            query = query.filter_by(is_active=False)
            
        # Order by created_at desc
        testimonials = query.order_by(Testimonial.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'testimonials': [{
                'id': t.id,
                'name': t.name,
                'title': t.title,
                'company': t.company,
                'avatarUrl': t.avatar_url,
                'content': t.content,
                'rating': t.rating,
                'isFeatured': t.is_featured,
                'isActive': t.is_active,
                'countryCode': t.country_code,
                'createdAt': t.created_at.isoformat()
            } for t in testimonials.items],
            'total': testimonials.total,
            'pages': testimonials.pages,
            'currentPage': page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_testimonials_bp.route('/content/testimonials', methods=['POST'])
@admin_required
def create_testimonial():
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('name') or not data.get('content'):
            return jsonify({'error': 'Name and Content are required'}), 400
            
        testimonial = Testimonial(
            name=data['name'],
            title=data.get('title'),
            company=data.get('company'),
            avatar_url=data.get('avatarUrl'),
            content=data['content'],
            rating=data.get('rating', 5),
            is_featured=data.get('isFeatured', False),
            is_active=data.get('isActive', True),
            country_code=data.get('countryCode')
        )
        
        db.session.add(testimonial)
        db.session.commit()
        
        log_audit('TESTIMONIAL_CREATE', 'testimonial', str(testimonial.id), {
            'name': testimonial.name
        })
        
        return jsonify({
            'ok': True,
            'id': testimonial.id,
            'message': 'Testimonial created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_testimonials_bp.route('/content/testimonials/<int:id>', methods=['PUT'])
@admin_required
def update_testimonial(id):
    try:
        testimonial = Testimonial.query.get_or_404(id)
        data = request.get_json()
        
        if 'name' in data:
            testimonial.name = data['name']
        if 'title' in data:
            testimonial.title = data['title']
        if 'company' in data:
            testimonial.company = data['company']
        if 'avatarUrl' in data:
            testimonial.avatar_url = data['avatarUrl']
        if 'content' in data:
            testimonial.content = data['content']
        if 'rating' in data:
            testimonial.rating = data['rating']
        if 'isFeatured' in data:
            testimonial.is_featured = data['isFeatured']
        if 'isActive' in data:
            testimonial.is_active = data['isActive']
        if 'countryCode' in data:
            testimonial.country_code = data['countryCode']
            
        db.session.commit()
        
        log_audit('TESTIMONIAL_UPDATE', 'testimonial', str(id), data)
        
        return jsonify({'ok': True, 'message': 'Testimonial updated'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_testimonials_bp.route('/content/testimonials/<int:id>', methods=['DELETE'])
@admin_required
def delete_testimonial(id):
    try:
        testimonial = Testimonial.query.get_or_404(id)
        
        # Hard delete for now, or could implement soft delete if preferred
        # Since it's content, hard delete is usually fine unless we want to archive
        db.session.delete(testimonial)
        
        log_audit('TESTIMONIAL_DELETE', 'testimonial', str(id))
        db.session.commit()
        
        return jsonify({'ok': True, 'message': 'Testimonial deleted'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
