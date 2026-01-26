"""
Admin User Management Routes
CRUD for /api/admin/users
"""
import bcrypt
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from models import db, User, Role, LoginEvent, UserActivity

users_bp = Blueprint('admin_users', __name__)


from ..decorators import admin_required


@users_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """List all users"""
    try:
        country = getattr(request, 'user_country', 'US')
        users = User.query.filter_by(country_code=country).order_by(User.created_at.desc()).limit(500).all()
        return jsonify({
            'users': [u.to_dict() for u in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@users_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get single user full profile"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Fetch login history
        logins = LoginEvent.query.filter_by(user_id=user_id).order_by(LoginEvent.created_at.desc()).limit(10).all()
        
        # Fetch activity log
        activities = UserActivity.query.filter_by(user_id=user_id).order_by(UserActivity.created_at.desc()).limit(50).all()
        
        user_data = user.to_dict()
        
        # Append extra admin-only fields to user_data if not present
        user_data['lastLoginIp'] = logins[0].ip_address if logins else None
        
        return jsonify({
            'profile': user_data,
            'loginHistory': [{
                'id': l.id,
                'date': l.created_at.isoformat() if l.created_at else None,
                'ip': l.ip_address,
                'userAgent': l.user_agent,
                'success': l.success,
                'location': l.location
            } for l in logins],
            'activityLog': [{
                'id': a.id,
                'action': a.action,
                'date': a.created_at.isoformat() if a.created_at else None,
                'details': a.details,
                'ip': a.ip_address
            } for a in activities]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    try:
        data = request.get_json()
        password = data.get('password')
        if not password:
            return jsonify({'error': 'Password is required'}), 400
            
        # Hash password
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        user = User(
            name=data.get('name'),
            email=data.get('email'),
            password=password_hash,
            role=data.get('role', 'user'),
            active=data.get('is_active', 1),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US')),
            created_at=datetime.now(timezone.utc)
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({'ok': True, 'id': user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>', methods=['PATCH'])
@admin_required
def update_user(user_id):
    """Update user"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        if 'name' in data:
            user.name = data['name']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.active = 1 if data['is_active'] else 0
        if 'is_verified' in data:
            user.email_verified = data['is_verified']
        
        user.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Delete user"""
    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# Roles endpoints
@users_bp.route('/roles', methods=['GET'])
@admin_required
def get_roles():
    """List all roles"""
    try:
        roles = Role.query.all()
        return jsonify({
            'roles': [{
                'id': r.id,
                'name': r.name,
                'description': r.description,
                'permissions': r.permissions,
                'is_system': r.is_system,
            } for r in roles]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
