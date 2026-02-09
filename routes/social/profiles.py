"""
Social API Routes - User Profiles
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import joinedload
from models import db, User, UserProfile
from routes.decorators import auth_required

profiles_bp = Blueprint('profiles', __name__)


@profiles_bp.route('/profiles', methods=['GET'])
def list_public_profiles():
    """List public investor profiles"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    trading_style = request.args.get('trading_style')
    sort_by = request.args.get('sort_by', 'followers')  # followers, ideas, likes
    
    # Eager load user relationship to avoid N+1 queries
    query = UserProfile.query.options(
        joinedload(UserProfile.user)
    ).filter(UserProfile.profile_visibility == 'public')
    
    if trading_style:
        query = query.filter(UserProfile.trading_style == trading_style)
    
    # Sort options
    if sort_by == 'followers':
        query = query.order_by(UserProfile.followers_count.desc())
    elif sort_by == 'ideas':
        query = query.order_by(UserProfile.ideas_count.desc())
    elif sort_by == 'likes':
        query = query.order_by(UserProfile.likes_received.desc())
    else:
        query = query.order_by(UserProfile.followers_count.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    profiles = []
    for profile in pagination.items:
        user = profile.user  # Already loaded via joinedload
        profile_data = profile.to_dict()
        profile_data['user'] = {
            'name': user.name if profile.profile_visibility == 'public' else 'Anonymous',
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
        }
        profiles.append(profile_data)
    
    return jsonify({
        'profiles': profiles,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
    })


@profiles_bp.route('/profiles/<identifier>', methods=['GET'])
def get_public_profile(identifier):
    """Get a public profile by username or user ID"""
    # Try to find by public_username first
    profile = UserProfile.query.filter_by(public_username=identifier).first()
    
    # If not found by username, try by user_id
    if not profile:
        try:
            user_id = int(identifier)
            profile = UserProfile.query.filter_by(user_id=user_id).first()
        except (ValueError, TypeError):
            pass
    
    if not profile:
        return jsonify({'error': 'Profile not found'}), 404
    
    if profile.profile_visibility == 'private':
        return jsonify({'error': 'This profile is private'}), 403
    
    user = profile.user
    
    profile_data = profile.to_dict()
    
    if profile.profile_visibility == 'anonymous':
        profile_data['user'] = {
            'name': 'Anonymous Investor',
            'avatarUrl': None,
            'verifiedBadge': False,
        }
    else:
        profile_data['user'] = {
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
            'createdAt': user.created_at.isoformat() if user.created_at else None,
        }
    
    return jsonify({'profile': profile_data})


@profiles_bp.route('/profiles/me', methods=['GET'])
@auth_required
def get_my_profile():
    """Get current user's profile"""
    user = request.user
    
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    
    if not profile:
        # Create profile if doesn't exist
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
        db.session.commit()
    
    return jsonify({
        'profile': profile.to_dict(include_private=True),
        'user': user.to_dict()
    })


@profiles_bp.route('/profiles/me', methods=['PUT'])
@auth_required
def update_my_profile():
    """Update current user's profile"""
    user = request.user
    data = request.get_json() or {}
    
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    
    if not profile:
        profile = UserProfile(user_id=user.id)
        db.session.add(profile)
    
    # Update fields
    if 'bio' in data:
        profile.bio = data['bio'][:500] if data['bio'] else None  # Limit bio length
    
    if 'tradingStyle' in data and data['tradingStyle'] in [
        'day_trader', 'swing_trader', 'long_term', 'value', 'growth', 'dividend', 'mixed'
    ]:
        profile.trading_style = data['tradingStyle']
    
    if 'publicUsername' in data:
        username = data['publicUsername']
        if username:
            # Validate username
            if len(username) < 3 or len(username) > 50:
                return jsonify({'error': 'Username must be 3-50 characters'}), 400
            if not username.isalnum() and '_' not in username:
                return jsonify({'error': 'Username can only contain letters, numbers, and underscores'}), 400
            # Check uniqueness
            existing = UserProfile.query.filter(
                UserProfile.public_username == username,
                UserProfile.user_id != user.id
            ).first()
            if existing:
                return jsonify({'error': 'Username already taken'}), 400
            profile.public_username = username
        else:
            profile.public_username = None
    
    if 'profileVisibility' in data and data['profileVisibility'] in ['public', 'private', 'anonymous']:
        profile.profile_visibility = data['profileVisibility']
    
    if 'showPortfolio' in data:
        profile.show_portfolio = bool(data['showPortfolio'])
    
    if 'showPerformance' in data:
        profile.show_performance = bool(data['showPerformance'])
    
    if 'showTrades' in data:
        profile.show_trades = bool(data['showTrades'])
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'profile': profile.to_dict(include_private=True)
    })


@profiles_bp.route('/profiles/check-username/<username>', methods=['GET'])
def check_username_availability(username):
    """Check if username is available"""
    if len(username) < 3 or len(username) > 50:
        return jsonify({'available': False, 'error': 'Username must be 3-50 characters'})
    
    existing = UserProfile.query.filter_by(public_username=username).first()
    
    return jsonify({
        'available': existing is None,
        'username': username
    })
