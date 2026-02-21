from functools import wraps
from flask import request, jsonify, g
import jwt
from config import config
from services.settings_service import get_setting_secure
from models import User, ApiKey, ApiUsageLog, UserSubscription, db
from models.user import UserSession
import bcrypt
import time
from datetime import datetime, timezone

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Allow OPTIONS preflight requests to pass through for CORS
        if request.method == 'OPTIONS':
            return '', 200
            
        auth_header = request.headers.get('Authorization', '')
        
        # DEBUG: Log full request context for auth debugging
        print(f'[AUTH DEBUG] {request.method} {request.path} | Origin: {request.headers.get("Origin", "none")} | Auth: {auth_header[:80] if auth_header else "EMPTY"}')
        
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        
        # Debug: Show token info
        print(f'[AUTH DEBUG] Token received: {token[:20]}...{token[-20:] if len(token) > 40 else ""}')
        
        try:
            jwt_secret = get_setting_secure('JWT_SECRET', config.JWT_SECRET)
            payload = jwt.decode(token, jwt_secret, algorithms=['HS256'])
            print(f'[AUTH DEBUG] Token decoded successfully. User ID: {payload.get("user_id")}')
            user = User.query.get(payload['user_id'])
            
            if not user:
                print(f'[AUTH DEBUG] User not found for ID: {payload.get("user_id")}')
                return jsonify({'error': 'User not found'}), 404

            # validate session 
            session = UserSession.query.filter_by(
                user_id=user.id,
                token=token
            ).first()
            
            if not session:
                print(f'[AUTH DEBUG] Invalid session for user ID: {user.id}')
                return jsonify({'error': 'Invalid session or expired'}), 401
            
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


def _get_client_ip() -> str:
    """Extract the real client IP from proxy headers, safe for VARCHAR(45)."""
    ip = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        or request.headers.get('X-Real-IP')
        or request.remote_addr
        or 'Unknown'
    )
    return ip[:45]

def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
            
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return jsonify({'error': 'No API key provided. Format: Bearer <key>'}), 401
            
        raw_key = auth_header.split(' ')[1]
        
        # A valid key must be at least 8 characters
        if len(raw_key) < 8:
            return jsonify({'error': 'Invalid API key format'}), 401
            
        key_prefix = raw_key[:8]
        
        # Find potential keys by prefix
        api_keys = ApiKey.query.filter_by(key_prefix=key_prefix, is_active=True).all()
        
        valid_key = None
        for k in api_keys:
            if bcrypt.checkpw(raw_key.encode('utf-8'), k.key_hash.encode('utf-8')):
                valid_key = k
                break
                
        if not valid_key:
            return jsonify({'error': 'Invalid or inactive API key'}), 401
            
        # Check expiry
        if valid_key.expires_at and valid_key.expires_at < datetime.now(timezone.utc):
            return jsonify({'error': 'API key has expired'}), 401
            
        # Set context variables
        user = User.query.get(valid_key.user_id)
        if not user or user.account_status != 'active':
            return jsonify({'error': 'Associated user account is not active'}), 403
            
        # Determine Daily API Limit
        daily_limit = 50 # Default Free Tier
        
        # Check for active subscription
        active_sub = UserSubscription.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if active_sub and active_sub.plan and active_sub.plan.features:
            features = active_sub.plan.features
            if isinstance(features, dict) and 'api_daily_limit' in features:
                daily_limit = int(features['api_daily_limit'])
        
        # Count usage today
        today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Get all keys belonging to this user
        user_keys = ApiKey.query.filter_by(user_id=user.id).all()
        key_ids = [k.id for k in user_keys]
        
        today_usage = 0
        if key_ids:
            today_usage = ApiUsageLog.query.filter(
                ApiUsageLog.api_key_id.in_(key_ids),
                ApiUsageLog.created_at >= today
            ).count()
            
        if today_usage >= daily_limit:
            return jsonify({
                'error': 'Daily API Limit Exceeded',
                'message': f'You have reached your limit of {daily_limit} requests/day. Upgrade your plan to increase limits.',
                'status': 429
            }), 429
            
        request.user = user
        g.user = user
        g.api_key = valid_key
        
        start_time = time.time()
        
        # Execute the route
        try:
            response = f(*args, **kwargs)
        except Exception as e:
            # Log failure
            duration_ms = int((time.time() - start_time) * 1000)
            log = ApiUsageLog(
                api_key_id=valid_key.id,
                endpoint=request.path,
                method=request.method,
                status_code=500,
                ip_address=_get_client_ip(),
                duration_ms=duration_ms
            )
            db.session.add(log)
            db.session.commit()
            raise e
            
        # Ensure response is a tuple to extract status code
        status_code = 200
        if isinstance(response, tuple) and len(response) > 1:
            status_code = response[1]
        elif hasattr(response, 'status_code'):
            status_code = response.status_code
            
        # Log success
        duration_ms = int((time.time() - start_time) * 1000)
        log = ApiUsageLog(
            api_key_id=valid_key.id,
            endpoint=request.path,
            method=request.method,
            status_code=status_code,
            ip_address=_get_client_ip(),
            duration_ms=duration_ms
        )
        valid_key.last_used_at = datetime.now(timezone.utc)
        
        db.session.add(log)
        db.session.commit()
        
        return response
        
    return decorated
