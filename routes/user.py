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
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    # Track profile update activity
    try:
        from handlers import track_profile_update
        changed_fields = [k for k in ['name', 'phone', 'avatarUrl'] if k in data]
        track_profile_update(user.id, changed_fields)
    except Exception as e:
        print(f'[User] Activity tracking failed: {e}')
    
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
    """Get user's net worth calculated from portfolio holdings"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    from models import UserPortfolio, PortfolioHolding
    
    # Get all user portfolios
    portfolios = UserPortfolio.query.filter_by(user_id=user.id).all()
    
    total_value = 0
    total_cost = 0
    total_gain = 0
    
    for portfolio in portfolios:
        holdings = PortfolioHolding.query.filter_by(portfolio_id=portfolio.id).all()
        for h in holdings:
            shares = float(h.shares or 0)
            avg_price = float(h.avg_buy_price or 0)
            current_price = float(h.current_price or 0)
            
            value = shares * current_price
            cost = shares * avg_price
            
            total_value += value
            total_cost += cost
            total_gain += (value - cost)
    
    # Calculate percentage change
    change_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
    
    return jsonify({
        'netWorth': round(total_value, 2),
        'netWorthChange': round(total_gain, 2),
        'netWorthChangePercent': round(change_percent, 2),
        'portfolioCount': len(portfolios)
    })
