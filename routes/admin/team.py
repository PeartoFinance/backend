"""
Admin Team Management Routes
CRUD for /api/admin/team
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
from models import db, TeamMember

team_bp = Blueprint('admin_team', __name__)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@team_bp.route('/team', methods=['GET'])
@admin_required
def get_team_members():
    """List all team members"""
    try:
        members = TeamMember.query.order_by(TeamMember.sort_order).all()
        return jsonify({
            'team': [{
                'id': m.id,
                'name': m.name,
                'title': m.title,
                'bio': m.bio,
                'photo_url': m.photo_url,
                'email': m.email,
                'linkedin': m.linkedin,
                'twitter': m.twitter,
                'is_active': m.is_active,
                'sort_order': m.sort_order,
                'created_at': m.created_at.isoformat() if m.created_at else None,
            } for m in members]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/<int:member_id>', methods=['GET'])
@admin_required
def get_team_member(member_id):
    """Get single team member"""
    try:
        member = TeamMember.query.get_or_404(member_id)
        return jsonify({
            'id': member.id,
            'name': member.name,
            'title': member.title,
            'bio': member.bio,
            'photo_url': member.photo_url,
            'email': member.email,
            'linkedin': member.linkedin,
            'twitter': member.twitter,
            'is_active': member.is_active,
            'sort_order': member.sort_order,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team', methods=['POST'])
@admin_required
def create_team_member():
    """Create team member"""
    try:
        data = request.get_json()
        member = TeamMember(
            name=data.get('name'),
            title=data.get('title'),
            bio=data.get('bio'),
            photo_url=data.get('photo_url'),
            email=data.get('email'),
            linkedin=data.get('linkedin'),
            twitter=data.get('twitter'),
            is_active=data.get('is_active', True),
            sort_order=data.get('sort_order', 0),
            created_at=datetime.utcnow()
        )
        db.session.add(member)
        db.session.commit()
        return jsonify({'ok': True, 'id': member.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/<int:member_id>', methods=['PUT'])
@admin_required
def update_team_member(member_id):
    """Update team member"""
    try:
        member = TeamMember.query.get_or_404(member_id)
        data = request.get_json()
        
        for field in ['name', 'title', 'bio', 'photo_url', 'email', 'linkedin', 'twitter', 'is_active', 'sort_order']:
            if field in data:
                setattr(member, field, data[field])
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/<int:member_id>', methods=['DELETE'])
@admin_required
def delete_team_member(member_id):
    """Delete team member"""
    try:
        member = TeamMember.query.get_or_404(member_id)
        db.session.delete(member)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@team_bp.route('/team/reorder', methods=['POST'])
@admin_required
def reorder_team():
    """Reorder team members"""
    try:
        data = request.get_json()
        order = data.get('order', [])  # List of {id, sort_order}
        
        for item in order:
            TeamMember.query.filter_by(id=item['id']).update(
                {'sort_order': item['sort_order']}, synchronize_session=False
            )
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
