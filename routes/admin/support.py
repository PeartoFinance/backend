"""
Admin Support Routes - Contact messages, support
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, ContactMessage
from datetime import datetime

support_bp = Blueprint('admin_support', __name__)


@support_bp.route('/contact-messages', methods=['GET'])
@permission_required("communications")
def get_contact_messages():
    """List all contact messages (country-filtered)"""
    try:
        status = request.args.get('status')
        country = getattr(request, 'user_country', 'US')
        query = ContactMessage.query.filter(
            (ContactMessage.country_code == country) | 
            (ContactMessage.country_code == 'GLOBAL')
        ).order_by(ContactMessage.created_at.desc())
        if status:
            query = query.filter(ContactMessage.status == status)
        msgs = query.limit(500).all()
        return jsonify({
            'messages': [{
                'id': m.id,
                'name': m.name,
                'email': m.email,
                'phone': m.phone,
                'subject': m.subject,
                'message': m.message,
                'status': m.status,
                'country_code': m.country_code,
                'created_at': m.created_at.isoformat() if m.created_at else None,
                'replied_at': m.replied_at.isoformat() if m.replied_at else None
            } for m in msgs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@support_bp.route('/contact-messages/<id>', methods=['PUT', 'PATCH'])
@permission_required("communications")
def update_contact_message(id):
    """Update message status (mark as read, replied)"""
    try:
        msg = ContactMessage.query.get_or_404(id)
        data = request.get_json()
        if 'status' in data:
            msg.status = data['status']
            if data['status'] == 'replied':
                msg.replied_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@support_bp.route('/contact-messages/<id>', methods=['DELETE'])
@permission_required("communications")
def delete_contact_message(id):
    """Delete a contact message"""
    try:
        msg = ContactMessage.query.get_or_404(id)
        db.session.delete(msg)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
