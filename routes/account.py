"""
Account Management API Routes
- Account status, deactivation, reactivation, deletion
Based on old/Frontend/server/src/accountApi.js
"""
from flask import Blueprint, request, jsonify
import bcrypt
from datetime import datetime
from models import db, User, UserSession
from .decorators import auth_required

account_bp = Blueprint('account', __name__)


@account_bp.route('/status', methods=['GET'])
@auth_required
def get_account_status():
    """Get current account status"""
    user = request.user
    return jsonify({
        'status': user.account_status or 'active',
        'deactivatedAt': user.deactivated_at.isoformat() if user.deactivated_at else None,
        'deactivationReason': user.deactivation_reason,
        'createdAt': user.created_at.isoformat() if user.created_at else None
    })


@account_bp.route('/deactivate', methods=['POST'])
@auth_required
def deactivate_account():
    """Deactivate user account"""
    user = request.user
    data = request.get_json()
    password = data.get('password', '')
    reason = data.get('reason', 'User requested')
    
    if not password:
        return jsonify({'error': 'Password required for deactivation'}), 400
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401
    
    # Check current status
    if user.account_status == 'deactivated':
        return jsonify({'error': 'Account is already deactivated'}), 400
    
    # Deactivate account
    user.account_status = 'deactivated'
    user.deactivated_at = datetime.utcnow()
    user.deactivation_reason = reason
    
    # Revoke all active sessions
    UserSession.query.filter_by(user_id=user.id).delete()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account deactivated successfully. You will be logged out shortly.'
    })


@account_bp.route('/reactivate', methods=['POST'])
def reactivate_account():
    """Reactivate deactivated account"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Get user
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401
    
    # Check current status
    if user.account_status != 'deactivated':
        return jsonify({'error': 'Account is not deactivated'}), 400
    
    # Reactivate account
    user.account_status = 'active'
    user.deactivated_at = None
    user.deactivation_reason = None
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account reactivated successfully. You can now log in.'
    })


@account_bp.route('/delete-permanently', methods=['POST'])
@auth_required
def delete_account_permanently():
    """Permanently delete account (soft delete)"""
    user = request.user
    data = request.get_json()
    password = data.get('password', '')
    confirmation = data.get('confirmation', '')
    
    if not password or confirmation != 'DELETE':
        return jsonify({'error': 'Password and confirmation "DELETE" required'}), 400
    
    # Verify password
    if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        return jsonify({'error': 'Invalid password'}), 401
    
    # Soft delete - mark as deleted
    user.account_status = 'deleted'
    user.deactivated_at = datetime.utcnow()
    user.deactivation_reason = 'Permanent deletion requested'
    
    # Revoke all sessions
    UserSession.query.filter_by(user_id=user.id).delete()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Account has been permanently deleted.'
    })
