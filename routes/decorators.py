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
            print(f'[AUTH DEBUG] No Bearer token. Header: {auth_header[:50]}...' if auth_header else '[AUTH DEBUG] No Authorization header')
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Debug: Show token info
        print(f'[AUTH DEBUG] Token received: {token[:20]}...{token[-20:] if len(token) > 40 else ""}')
        
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
            print(f'[AUTH DEBUG] Token decoded successfully. User ID: {payload.get("user_id")}')
            user = User.query.get(payload['user_id'])
            
            if not user:
                print(f'[AUTH DEBUG] User not found for ID: {payload.get("user_id")}')
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
            print(f'[AUTH DEBUG] Token expired')
            return jsonify({'error': 'Token expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f'[AUTH DEBUG] Invalid token error: {str(e)}')
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
