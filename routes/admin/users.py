"""
Admin User Management Routes
CRUD for /api/admin/users
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from .auth import admin_required
from models import db, User, Role

users_bp = Blueprint('admin_users', __name__)


@users_bp.route('/users', methods=['GET'])
@admin_required
def get_users():
    """List all users"""
    try:
        users = User.query.order_by(User.created_at.desc()).limit(500).all()
        return jsonify({
            'users': [{
                'id': u.id,
                'name': u.name,
                'email': u.email,
                'role': u.role,
                'is_active': u.is_active,
                'is_verified': u.is_verified,
                'avatar_url': u.avatar_url,
                'created_at': u.created_at.isoformat() if u.created_at else None,
            } for u in users]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):
    """Get single user"""
    try:
        user = User.query.get_or_404(user_id)
        return jsonify({
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role,
            'is_active': user.is_active,
            'is_verified': user.is_verified,
            'avatar_url': user.avatar_url,
            'phone': user.phone,
            'country_code': user.country_code,
            'created_at': user.created_at.isoformat() if user.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@users_bp.route('/users', methods=['POST'])
@admin_required
def create_user():
    """Create new user"""
    try:
        data = request.get_json()
        user = User(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=data.get('password', ''),  # Should hash this
            role=data.get('role', 'user'),
            is_active=data.get('is_active', True),
            country_code=data.get('country_code', 'US'),
            created_at=datetime.utcnow()
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
            user.is_active = data['is_active']
        if 'is_verified' in data:
            user.is_verified = data['is_verified']
        
        user.updated_at = datetime.utcnow()
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
