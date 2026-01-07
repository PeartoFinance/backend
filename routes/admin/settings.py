"""
Admin Settings Routes
CRUD for /api/admin/settings
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from datetime import datetime
from models import db, Settings, Appearance

settings_bp = Blueprint('admin_settings', __name__)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


# ============ SETTINGS ============

@settings_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """List all settings"""
    try:
        settings = Settings.query.all()
        return jsonify({
            'settings': [{
                'id': s.id,
                'key': s.key,
                'value': s.value,
                'category': s.category,
                'description': s.description,
            } for s in settings]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/settings', methods=['POST'])
@admin_required
def create_setting():
    """Create setting"""
    try:
        data = request.get_json()
        setting = Settings(
            key=data.get('key'),
            value=data.get('value'),
            category=data.get('category'),
            description=data.get('description'),
        )
        db.session.add(setting)
        db.session.commit()
        return jsonify({'ok': True, 'id': setting.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/settings/<int:setting_id>', methods=['PUT'])
@admin_required
def update_setting(setting_id):
    """Update setting"""
    try:
        setting = Settings.query.get_or_404(setting_id)
        data = request.get_json()
        
        if 'key' in data:
            setting.key = data['key']
        if 'value' in data:
            setting.value = data['value']
        if 'category' in data:
            setting.category = data['category']
        if 'description' in data:
            setting.description = data['description']
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/settings/<int:setting_id>', methods=['DELETE'])
@admin_required
def delete_setting(setting_id):
    """Delete setting"""
    try:
        setting = Settings.query.get_or_404(setting_id)
        db.session.delete(setting)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ APPEARANCE ============

@settings_bp.route('/appearance', methods=['GET'])
@admin_required
def get_appearance():
    """Get appearance settings"""
    try:
        themes = Appearance.query.all()
        return jsonify({
            'themes': [{
                'id': t.id,
                'name': t.name,
                'primary_color': t.primary_color,
                'secondary_color': t.secondary_color,
                'logo_url': t.logo_url,
                'is_active': t.is_active,
            } for t in themes]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/appearance/<int:appearance_id>', methods=['PUT'])
@admin_required
def update_appearance(appearance_id):
    """Update appearance setting"""
    try:
        appearance = Appearance.query.get_or_404(appearance_id)
        data = request.get_json()
        
        for field in ['name', 'primary_color', 'secondary_color', 'logo_url', 'is_active']:
            if field in data:
                setattr(appearance, field, data[field])
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
