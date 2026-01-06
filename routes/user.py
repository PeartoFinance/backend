"""
User Profile & Preferences API Routes
- Profile data, preferences, settings
Based on old/Frontend/server/src/userPreferencesApi.js
"""
from flask import Blueprint, request, jsonify
import bcrypt
from datetime import datetime
from models import db, User

user_bp = Blueprint('user', __name__)


def get_current_user():
    """Helper to get current user from email header"""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return None
    return User.query.filter_by(email=user_email).first()


@user_bp.route('/profile', methods=['GET'])
def get_profile():
    """Get current user profile"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify(user.to_dict())


@user_bp.route('/profile', methods=['PUT'])
def update_profile():
    """Update user profile"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    
    # Update allowed fields
    if 'name' in data and data['name']:
        user.name = data['name'].strip()
    
    if 'phone' in data:
        user.phone = data['phone']
    
    if 'avatarUrl' in data:
        user.avatar_url = data['avatarUrl']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@user_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'currency': user.currency or 'USD',
        'taxResidency': user.tax_residency or '',
        'languagePref': user.language_pref or 'en',
        'countryCode': user.country_code or 'US'
    })


@user_bp.route('/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    
    # Validate currency code
    currency = data.get('currency')
    if currency:
        import re
        if not re.match(r'^[A-Z]{3}$', currency):
            return jsonify({'error': 'Invalid currency code'}), 400
        user.currency = currency
    
    # Validate language code
    language_pref = data.get('languagePref')
    if language_pref:
        import re
        if not re.match(r'^[a-z]{2}$', language_pref):
            return jsonify({'error': 'Invalid language code'}), 400
        user.language_pref = language_pref
    
    # Update optional fields
    if 'taxResidency' in data:
        user.tax_residency = data['taxResidency']
    
    if 'countryCode' in data:
        user.country_code = data['countryCode']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Preferences updated successfully'
    })


@user_bp.route('/change-password', methods=['POST'])
def change_password():
    """Change user password"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    current_password = data.get('currentPassword', '')
    new_password = data.get('newPassword', '')
    
    if not current_password or not new_password:
        return jsonify({'error': 'Current and new password required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Verify current password
    if not bcrypt.checkpw(current_password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Current password is incorrect'}), 401
    
    # Update password
    user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    })
