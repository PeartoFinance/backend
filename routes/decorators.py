from functools import wraps
from flask import request, jsonify, g
import jwt
from config import config
from models import User

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS preflight requests to pass through for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
            user = User.query.get(payload['user_id'])
            
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            # Check account status
            if user.account_status != 'active':
                status_messages = {
                    'deleted': 'This account has been permanently deleted.',
                    'deactivated': 'Account is deactivated.',
                    'suspended': 'Account is suspended. Please contact support.'
                }
                msg = status_messages.get(user.account_status, 'Account is not active.')
                return jsonify({'error': msg}), 403
            
            # ✅ NEW (correct)
            g.user = user
            g.user_id = user.id
            g.user_country = getattr(user, 'country_code', 'US')
            
            # ✅ OLD (keep for compatibility)
            request.user = user
            
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
            
    return decorated

def admin_required(f):
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        if request.user.role != 'admin':
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated
