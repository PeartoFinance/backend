"""
User Profile & Preferences API Routes
- Profile data, preferences, settings
Based on old/Frontend/server/src/userPreferencesApi.js
"""
from flask import Blueprint, request, jsonify
import bcrypt
from datetime import datetime
import jwt
from config import config
from models import db, User, UserPortfolio, UserWatchlist, MarketData

user_bp = Blueprint('user', __name__)


def get_current_user():
    """Resolve current user from Authorization Bearer JWT or X-User-Email header.

    Priority:
    1. Authorization: Bearer <token> (JWT with `user_id` claim)
    2. X-User-Email header (compatibility fallback)
    """
    # If another middleware/decorator already set request.user, use it
    if hasattr(request, 'user') and getattr(request, 'user'):
        return request.user

    # Try Bearer token
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.split(' ', 1)[1].strip()
        try:
            payload = jwt.decode(token, config.JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if user_id:
                user = User.query.get(user_id)
                if user:
                    return user
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            # Invalid token -> fall through to header fallback
            pass

    # Compatibility fallback: X-User-Email
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        user = None
    else:
        user = User.query.filter_by(email=user_email).first()

    # Final Security Check: If user was found by any method, check their status
    if user and user.account_status != 'active':
        return None  # Treat as unauthenticated if account is not active
        
    return user


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
    
    # Profile customization fields
    if 'specializations' in data:
        user.specializations = data['specializations']
    
    if 'certifications' in data:
        user.certifications = data['certifications']
    
    if 'hourlyRate' in data:
        user.hourly_rate = data['hourlyRate']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Track profile update activity
    try:
        from handlers import track_profile_update
        changed_fields = [k for k in ['name', 'phone', 'avatarUrl', 'specializations', 'certifications', 'hourlyRate'] if k in data]
        track_profile_update(user.id, changed_fields)
    except Exception as e:
        print(f'[User] Activity tracking failed: {e}')
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    })


@user_bp.route('/referrals', methods=['GET'])
def get_referrals():
    """Get list of users referred by the current user"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Find all users where referred_by matches current user's ID
    referred_users = User.query.filter_by(referred_by=user.id).all()
    
    referrals_list = []
    for ru in referred_users:
        referrals_list.append({
            'id': ru.id,
            'name': ru.name,
            'email': f"{ru.email[:3]}***@{ru.email.split('@')[1]}", # Mask email for privacy
            'createdAt': ru.created_at.isoformat() if ru.created_at else None,
            'status': ru.account_status
        })
    
    return jsonify({
        'referralCode': user.referral_code,
        'totalReferrals': len(referred_users),
        'totalRewardPoints': user.total_reward_points,
        'referrals': referrals_list
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
    
    # Track settings update activity
    try:
        from handlers import track_settings_update
        track_settings_update(user.id, 'preferences')
    except Exception as e:
        print(f'[User] Activity tracking failed: {e}')
    
    return jsonify({
        'success': True,
        'message': 'Preferences updated successfully'
    })


@user_bp.route('/notification-preferences', methods=['GET'])
def get_notification_preferences():
    """Get user notification preferences"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    from models import UserNotificationPref
    from services.preference_checker import get_default_preferences
    
    prefs = UserNotificationPref.query.filter_by(user_id=user.id).first()
    
    if not prefs:
        # Return defaults if no preferences set
        return jsonify(get_default_preferences())
    
    return jsonify(prefs.to_dict())


@user_bp.route('/notification-preferences', methods=['PUT'])
def update_notification_preferences():
    """Update user notification preferences"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    from models import UserNotificationPref
    from datetime import time as dt_time
    
    data = request.get_json()
    
    prefs = UserNotificationPref.query.filter_by(user_id=user.id).first()
    if not prefs:
        prefs = UserNotificationPref(user_id=user.id)
        db.session.add(prefs)
    
    # Map frontend field names to database field names
    field_mapping = {
        'emailSecurity': 'email_security',
        'emailAccount': 'email_account',
        'emailPriceAlerts': 'email_price_alerts',
        'emailDailyDigest': 'email_daily_digest',
        'emailEarnings': 'email_earnings',
        'emailNews': 'email_news',
        'emailMarketing': 'email_marketing',
        'emailNewsletter': 'email_newsletter',
        'pushSecurity': 'push_security',
        'pushPriceAlerts': 'push_price_alerts',
        'pushNews': 'push_news',
        'pushEarnings': 'push_earnings',
        'smsSecurity': 'sms_security',
        'smsPriceAlerts': 'sms_price_alerts',
        'quietHoursEnabled': 'quiet_hours_enabled',
    }
    
    for frontend_key, db_key in field_mapping.items():
        if frontend_key in data:
            setattr(prefs, db_key, data[frontend_key])
    
    # Handle quiet hours time fields
    if 'quietHoursStart' in data and data['quietHoursStart']:
        try:
            parts = data['quietHoursStart'].split(':')
            prefs.quiet_hours_start = dt_time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass
    
    if 'quietHoursEnd' in data and data['quietHoursEnd']:
        try:
            parts = data['quietHoursEnd'].split(':')
            prefs.quiet_hours_end = dt_time(int(parts[0]), int(parts[1]))
        except (ValueError, IndexError):
            pass
    
    db.session.commit()
    
    # Track settings update activity
    try:
        from handlers import track_settings_update
        track_settings_update(user.id, 'notification_preferences')
    except Exception as e:
        print(f'[User] Activity tracking failed: {e}')
    
    return jsonify({
        'success': True,
        'message': 'Notification preferences updated',
        'preferences': prefs.to_dict()
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
    
    # Track password change activity
    try:
        from handlers import track_password_change
        track_password_change(user.id)
    except Exception as e:
        print(f'[User] Activity tracking failed: {e}')
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    })


@user_bp.route('/portfolio', methods=['GET'])
def get_user_portfolio_summary():
    """Return current user's portfolios summary for /api/user/portfolio."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    portfolios = UserPortfolio.query.filter_by(user_id=user.id).all()
    return jsonify({
        'portfolios': [p.to_dict() for p in portfolios]
    })


@user_bp.route('/watchlist', methods=['GET'])
def get_user_watchlist():
    """Return current user's watchlist symbols with basic quote info."""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    user_symbols = UserWatchlist.query.filter_by(user_id=user.id).all()
    symbols = [w.symbol for w in user_symbols]

    if not symbols:
        return jsonify({'items': []})

    prices = MarketData.query.filter(
        MarketData.symbol.in_(symbols)
    ).all()
    price_by_symbol = {p.symbol: p for p in prices}

    items = []
    for w in user_symbols:
        p = price_by_symbol.get(w.symbol)
        items.append({
            'symbol': w.symbol,
            'addedAt': w.added_at.isoformat() if w.added_at else None,
            'price': float(p.price) if p and p.price else None,
            'change': float(p.change) if p and p.change else None,
            'changePercent': float(p.change_percent) if p and p.change_percent else None,
        })

    return jsonify({'items': items})


@user_bp.route('/net-worth', methods=['GET'])
def get_net_worth():
    """Get user's net worth calculated from portfolio holdings using LIVE market data"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    from models import UserPortfolio, PortfolioHolding, MarketData
    
    # Get all user portfolios
    portfolios = UserPortfolio.query.filter_by(user_id=user.id).all()
    
    # Gather all holdings and their symbols
    all_holdings = PortfolioHolding.query.join(UserPortfolio).filter(UserPortfolio.user_id == user.id).all()
    symbols = set(h.symbol for h in all_holdings)
    
    # Fetch LIVE prices from MarketData (same as /portfolio/list does)
    market_map = {}
    if symbols:
        market_data = MarketData.query.filter(MarketData.symbol.in_(symbols)).all()
        for md in market_data:
            market_map[md.symbol] = float(md.price) if md.price is not None else 0
    
    total_value = 0
    total_cost = 0
    
    for h in all_holdings:
        shares = float(h.shares or 0)
        avg_price = float(h.avg_buy_price or 0)
        # Use LIVE price from MarketData, fallback to stored current_price
        current_price = market_map.get(h.symbol, float(h.current_price or 0))
        
        value = shares * current_price
        cost = shares * avg_price
        
        total_value += value
        total_cost += cost
    
    total_gain = total_value - total_cost
    
    # Calculate percentage change
    change_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
    
    return jsonify({
        'netWorth': round(total_value, 2),
        'netWorthChange': round(total_gain, 2),
        'netWorthChangePercent': round(change_percent, 2),
        'portfolioCount': len(portfolios)
    })


# ==========================================================
# SUBSCRIPTION & FEATURE USAGE ENDPOINTS
# Purpose: Power the frontend feature gating system
# ==========================================================

@user_bp.route('/subscription', methods=['GET'])
def get_user_subscription():
    """
    Returns the current user's subscription status and feature usage.
    This powers the frontend's feature gating system AND the billing page.
    """
    from models.subscription import UserSubscription
    from models.feature_usage import UserFeatureUsage
    from services.subscription.constants import UsageLimits
    
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user.id
    
    # Get user's subscription
    sub = UserSubscription.query.filter(
        UserSubscription.user_id == user_id, 
        UserSubscription.status.in_(['active', 'trialing'])
    ).first()
    
    if not sub or not sub.plan:
        # No subscription = Free tier defaults
        return jsonify({
            'has_subscription': False,
            'plan_name': 'Free',
            'plan_id': None,
            'status': 'active',
            'expires_at': None,
            'subscription': None,  # For billing page compatibility
            'features': {
                'portfolio_tracking': True,
                'real_time_data': True,
                'advanced_charts': False,
                'ai_insights': False,
                'download_reports': False,
                'unlimited_alerts': False,
                'priority_support': False,
            },
            'usage': _get_usage_for_plan(user_id, UsageLimits.FREE_DEFAULTS)
        })
    
    plan = sub.plan
    features = plan.features or {}
    
    # Extract boolean features and numeric limits separately
    boolean_features = {k: v for k, v in features.items() if isinstance(v, bool)}
    limit_features = {k: v for k, v in features.items() if isinstance(v, (int, float))}
    
    # Build subscription object for billing page
    subscription_data = {
        'id': sub.id,
        'status': sub.status,
        'auto_renew': sub.auto_renew if hasattr(sub, 'auto_renew') else True,
        'start_date': sub.created_at.isoformat() if hasattr(sub, 'created_at') and sub.created_at else None,
        'current_period_end': sub.current_period_end.isoformat() if sub.current_period_end else None,
        'plan': {
            'id': plan.id,
            'name': plan.name,
            'price': float(plan.price),
            'currency': plan.currency or 'USD',
            'interval': plan.interval if hasattr(plan, 'interval') else 'month',
        }
    }
    
    return jsonify({
        'has_subscription': True,
        'plan_name': plan.name,
        'plan_id': plan.id,
        'status': sub.status,
        'expires_at': sub.current_period_end.isoformat() if sub.current_period_end else None,
        'subscription': subscription_data,  # For billing page
        'features': boolean_features,
        'usage': _get_usage_for_plan(user_id, limit_features)
    })


def _get_usage_for_plan(user_id: int, limits: dict) -> dict:
    """Build usage response with current counts and remaining."""
    from models.feature_usage import UserFeatureUsage
    from services.subscription.constants import UsageLimits
    
    usage_response = {}
    
    for key, limit_value in limits.items():
        if not key.endswith('_limit'):
            continue
        
        usage = UserFeatureUsage.get_or_create(user_id, key)
        period = UsageLimits.PERIODS.get(key, 'daily')
        usage.reset_if_needed(period)
        
        if limit_value == -1:
            remaining = -1
        else:
            remaining = max(0, limit_value - usage.usage_count)
        
        usage_response[key] = {
            'limit': limit_value,
            'used': usage.usage_count,
            'remaining': remaining,
            'period': period,
        }
    
    return usage_response


@user_bp.route('/usage/<feature_key>', methods=['POST'])
def track_feature_usage(feature_key: str):
    """
    Increment usage for a feature and return updated counts.
    Called by frontend before performing a limited action.
    """
    from models.subscription import UserSubscription
    from models.feature_usage import UserFeatureUsage
    from services.subscription.constants import UsageLimits
    
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    user_id = user.id
    
    # Get user's subscription to find their limit
    sub = UserSubscription.query.filter(
        UserSubscription.user_id == user_id, 
        UserSubscription.status.in_(['active', 'trialing'])
    ).first()
    
    if sub and sub.plan and sub.plan.features:
        limit_value = sub.plan.features.get(feature_key, 0)
    else:
        limit_value = UsageLimits.FREE_DEFAULTS.get(feature_key, 0)
    
    # -1 means unlimited
    if limit_value == -1:
        return jsonify({
            'allowed': True,
            'remaining': -1,
            'message': 'Unlimited access'
        })
    
    usage = UserFeatureUsage.get_or_create(user_id, feature_key)
    period = UsageLimits.PERIODS.get(feature_key, 'daily')
    usage.reset_if_needed(period)
    
    # Check if limit exceeded
    if usage.usage_count >= limit_value:
        return jsonify({
            'allowed': False,
            'remaining': 0,
            'limit': limit_value,
            'message': f'You have reached your {period} limit. Upgrade to Pro for unlimited access.',
            'period': period,
        }), 429
    
    # Increment usage
    new_count = usage.increment()
    remaining = max(0, limit_value - new_count)
    
    return jsonify({
        'allowed': True,
        'remaining': remaining,
        'used': new_count,
        'limit': limit_value,
        'period': period,
    })

