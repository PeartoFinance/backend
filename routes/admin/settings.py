"""
Admin Settings Routes
CRUD for /api/admin/settings
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ..decorators import admin_required
from models import db, Settings, Appearance

settings_bp = Blueprint('admin_settings', __name__)


# ============ SETTINGS ============

@settings_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings():
    """List all settings"""
    try:
        country = getattr(request, 'user_country', 'US')
        settings = Settings.query.filter(
            (Settings.country_code == country) | 
            (Settings.country_code == 'GLOBAL')
        ).all()
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
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
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
        if 'country_code' in data:
            setting.country_code = data['country_code']
        
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
        country = getattr(request, 'user_country', 'US')
        themes = Appearance.query.filter(
            (Appearance.country_code == country) | 
            (Appearance.country_code == 'GLOBAL')
        ).all()
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
        
        for field in ['name', 'primary_color', 'secondary_color', 'logo_url', 'is_active', 'country_code']:
            if field in data:
                setattr(appearance, field, data[field])
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============ FEATURE FLAGS (Admin Toggles) ============

@settings_bp.route('/feature-flags', methods=['GET'])
@admin_required
def get_feature_flags():
    """Get all admin-controlled feature flags"""
    try:
        # Define known feature flags with defaults
        flags = {
            'ai_widgets_enabled': True,
            'ai_analysis_enabled': True,
            'maintenance_mode': False,
        }
        
        # Load actual values from settings table
        settings = Settings.query.filter(
            Settings.category == 'feature_flags'
        ).all()
        
        for s in settings:
            if s.type == 'boolean':
                flags[s.key] = s.value == 'true'
            else:
                flags[s.key] = s.value
        
        return jsonify({'flags': flags})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@settings_bp.route('/feature-flags/<flag_key>', methods=['PUT'])
@admin_required
def update_feature_flag(flag_key):
    """Update a feature flag (creates if doesn't exist)"""
    try:
        import uuid
        data = request.get_json()
        value = data.get('value')
        
        setting = Settings.query.filter_by(key=flag_key, category='feature_flags').first()
        
        if not setting:
            # Create new setting
            setting = Settings(
                id=str(uuid.uuid4()),
                key=flag_key,
                value=str(value).lower() if isinstance(value, bool) else str(value),
                type='boolean' if isinstance(value, bool) else 'string',
                category='feature_flags',
                description=f'Feature flag: {flag_key}',
                is_public=True,
                country_code='GLOBAL'
            )
            db.session.add(setting)
        else:
            setting.value = str(value).lower() if isinstance(value, bool) else str(value)
        
        db.session.commit()
        return jsonify({'ok': True, 'key': flag_key, 'value': value})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

