"""
Developer API Management Routes
"""
from flask import Blueprint, jsonify, request
from models import db, ApiKey, ApiUsageLog, UserSubscription
from .decorators import auth_required
import secrets
import bcrypt
from datetime import datetime, timezone, timedelta
from sqlalchemy import func

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/keys', methods=['GET'])
@auth_required
def get_keys():
    """List all API keys for the current user"""
    keys = ApiKey.query.filter_by(user_id=request.user.id).order_by(ApiKey.created_at.desc()).all()
    return jsonify([k.to_dict() for k in keys])

@developer_bp.route('/keys', methods=['POST'])
@auth_required
def generate_key():
    """Generate a new API key"""
    data = request.get_json() or {}
    name = data.get('name', 'My API Key').strip()
    
    # Generate the raw key: prefix (8 chars) + random (32 chars)
    raw_key = secrets.token_urlsafe(32)
    key_prefix = raw_key[:8]
    
    # Hash the key
    key_hash = bcrypt.hashpw(raw_key.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    new_key = ApiKey(
        user_id=request.user.id,
        name=name,
        key_prefix=key_prefix,
        key_hash=key_hash,
        is_active=True
    )
    
    db.session.add(new_key)
    db.session.commit()
    
    # Return the raw key ONLY ONCE
    result = new_key.to_dict()
    result['rawKey'] = raw_key
    
    return jsonify(result), 201

@developer_bp.route('/keys/<int:key_id>', methods=['DELETE'])
@auth_required
def revoke_key(key_id):
    """Revoke (deactivate) an API key"""
    key = ApiKey.query.filter_by(id=key_id, user_id=request.user.id).first()
    if not key:
        return jsonify({'error': 'Key not found'}), 404
        
    key.is_active = False
    db.session.commit()
    return jsonify({'success': True, 'message': 'API key revoked'})

@developer_bp.route('/usage', methods=['GET'])
@auth_required
def get_usage():
    """Get API usage statistics for the user"""
    # Get all keys for user
    keys = ApiKey.query.filter_by(user_id=request.user.id).all()
    key_ids = [k.id for k in keys]
    
    total_requests = 0
    today_requests = 0
    endpoints = {}
    
    if key_ids:
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        logs = ApiUsageLog.query.filter(
            ApiUsageLog.api_key_id.in_(key_ids),
            ApiUsageLog.created_at >= thirty_days_ago
        ).all()
        
        today = datetime.now(timezone.utc).date()
        for log in logs:
            total_requests += 1
            if log.created_at.date() == today:
                today_requests += 1
            if log.endpoint not in endpoints:
                endpoints[log.endpoint] = 0
            endpoints[log.endpoint] += 1
            
    # Calculate daily limit based on subscription
    daily_limit = 50 # Default free tier limit
    active_sub = UserSubscription.query.filter_by(
        user_id=request.user.id,
        status='active'
    ).first()
    
    if active_sub and active_sub.plan and active_sub.plan.features:
        features = active_sub.plan.features
        if isinstance(features, dict) and 'api_daily_limit' in features:
            daily_limit = int(features['api_daily_limit'])
            
    return jsonify({
        'totalRequests': total_requests,
        'todayRequests': today_requests,
        'dailyLimit': daily_limit,
        'endpoints': endpoints
    })
