from functools import wraps
from flask import request, jsonify
from .manager import SubscriptionManager

# ==========================================================
# SUBSCRIPTION DECORATORS
# Purpose: Reusable route guards to lock features behind plans.
# These decorators assume '@auth_required' has already run
# and 'request.user' is available.
# ==========================================================

def requires_feature(feature_key):
    """
    Decorator to protect routes based on subscription features.
    
    Usage:
    @portfolio_bp.route('/advanced-charts')
    @auth_required
    @requires_feature('advanced_analytics')
    def my_route():
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 1. Check if user exists (set by @auth_required)
            user = getattr(request, 'user', None)
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            # 2. Admin Override: Admins get access to everything bypass checks
            if getattr(user, 'is_admin', False) or getattr(user, 'role', '') == 'admin':
                return f(*args, **kwargs)
            
            # 3. Check Subscription Permission via Manager
            has_access = SubscriptionManager.check_access(user.id, feature_key)
            
            if not has_access:
                return jsonify({
                    'error': 'Subscription required',
                    'message': f"Your current plan does not include the '{feature_key}' feature. Please upgrade to access this.",
                    'feature_required': feature_key,
                    'action': 'upgrade'
                }), 403 # Forbidden
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def subscription_active(f):
    """
    Simpler decorator that just checks if the user has ANY active subscription.
    Useful for 'Member Only' sections that don't care about specific features.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = getattr(request, 'user', None)
        if not user:
             return jsonify({'error': 'Authentication required'}), 401
             
        # Admin bypass
        if getattr(user, 'is_admin', False) or getattr(user, 'role', '') == 'admin':
            return f(*args, **kwargs)

        sub = SubscriptionManager.get_user_subscription(user.id)
        if not sub:
            return jsonify({
                'error': 'Active subscription required',
                'action': 'subscribe'
            }), 402 # Payment Required
            
        return f(*args, **kwargs)
    return decorated_function
