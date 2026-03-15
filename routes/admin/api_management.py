from flask import Blueprint, jsonify, request
from models import db, ApiKey, ApiUsageLog, User
from ..decorators import admin_required, permission_required

admin_api_management_bp = Blueprint('admin_api_management', __name__)

@admin_api_management_bp.route('/api-management/keys', methods=['GET'])
@permission_required("apis_integration")
def get_all_keys():
    """List all API keys across the system"""
    try:
        keys = ApiKey.query.order_by(ApiKey.created_at.desc()).all()
        results = []
        for k in keys:
            user = User.query.get(k.user_id)
            results.append({
                'id': k.id,
                'userId': k.user_id,
                'userName': user.name if user else 'Unknown',
                'userEmail': user.email if user else 'Unknown',
                'name': k.name,
                'keyPrefix': k.key_prefix,
                'isActive': k.is_active,
                'createdAt': k.created_at.isoformat() if k.created_at else None,
                'expiresAt': k.expires_at.isoformat() if k.expires_at else None,
                'lastUsedAt': k.last_used_at.isoformat() if k.last_used_at else None
            })
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@admin_api_management_bp.route('/api-management/keys/<int:key_id>', methods=['DELETE'])
@permission_required("apis_integration")
def revoke_key(key_id):
    """Admin revoke API key"""
    try:
        key = ApiKey.query.get_or_404(key_id)
        db.session.delete(key)
        db.session.commit()
        return jsonify({'success': True, 'message': 'API Key revoked successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_api_management_bp.route('/api-management/usage', methods=['GET'])
@permission_required("apis_integration")
def get_global_usage():
    """Get global API usage stats"""
    try:
        total_requests = ApiUsageLog.query.count()
        return jsonify({'totalRequests': total_requests})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
