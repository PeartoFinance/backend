"""
Social API Routes - Follow System
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
from models import db, User, UserProfile, UserFollow
from routes.decorators import auth_required

follows_bp = Blueprint('follows', __name__)


@follows_bp.route('/follow/<int:user_id>', methods=['POST'])
@auth_required
def follow_user(user_id):
    """Follow a user"""
    current_user = request.user
    
    if current_user.id == user_id:
        return jsonify({'error': 'Cannot follow yourself'}), 400
    
    # Check if user exists
    target_user = User.query.get(user_id)
    if not target_user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if already following
    existing = UserFollow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    
    if existing:
        return jsonify({'error': 'Already following this user'}), 400
    
    # Create follow relationship
    follow = UserFollow(
        follower_id=current_user.id,
        following_id=user_id
    )
    db.session.add(follow)
    
    # Update follower/following counts
    my_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    target_profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if my_profile:
        my_profile.following_count = (my_profile.following_count or 0) + 1
    if target_profile:
        target_profile.followers_count = (target_profile.followers_count or 0) + 1
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Now following user'})


@follows_bp.route('/follow/<int:user_id>', methods=['DELETE'])
@auth_required
def unfollow_user(user_id):
    """Unfollow a user"""
    current_user = request.user
    
    follow = UserFollow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    
    if not follow:
        return jsonify({'error': 'Not following this user'}), 400
    
    db.session.delete(follow)
    
    # Update counts
    my_profile = UserProfile.query.filter_by(user_id=current_user.id).first()
    target_profile = UserProfile.query.filter_by(user_id=user_id).first()
    
    if my_profile and my_profile.following_count:
        my_profile.following_count = max(0, my_profile.following_count - 1)
    if target_profile and target_profile.followers_count:
        target_profile.followers_count = max(0, target_profile.followers_count - 1)
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Unfollowed user'})


@follows_bp.route('/follow/check/<int:user_id>', methods=['GET'])
@auth_required
def check_following(user_id):
    """Check if current user follows target user"""
    current_user = request.user
    
    follow = UserFollow.query.filter_by(
        follower_id=current_user.id,
        following_id=user_id
    ).first()
    
    return jsonify({'isFollowing': follow is not None})


@follows_bp.route('/follow/followers', methods=['GET'])
@auth_required
def get_my_followers():
    """Get current user's followers"""
    current_user = request.user
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    # Eager load follower user and their profile to avoid N+1
    follows = UserFollow.query.options(
        joinedload(UserFollow.follower).joinedload(User.profile)
    ).filter_by(following_id=current_user.id)\
        .order_by(UserFollow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    followers = []
    for f in follows.items:
        user = f.follower
        profile = user.profile  # Already loaded via joinedload
        followers.append({
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
            'tradingStyle': profile.trading_style if profile else None,
            'followedAt': f.created_at.isoformat() if f.created_at else None,
        })
    
    return jsonify({
        'followers': followers,
        'total': follows.total,
        'page': page,
        'pages': follows.pages,
    })


@follows_bp.route('/follow/following', methods=['GET'])
@auth_required
def get_my_following():
    """Get users current user is following"""
    current_user = request.user
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    # Eager load following user and their profile to avoid N+1
    follows = UserFollow.query.options(
        joinedload(UserFollow.following).joinedload(User.profile)
    ).filter_by(follower_id=current_user.id)\
        .order_by(UserFollow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    following = []
    for f in follows.items:
        user = f.following
        profile = user.profile  # Already loaded via joinedload
        following.append({
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
            'tradingStyle': profile.trading_style if profile else None,
            'followedAt': f.created_at.isoformat() if f.created_at else None,
        })
    
    return jsonify({
        'following': following,
        'total': follows.total,
        'page': page,
        'pages': follows.pages,
    })


@follows_bp.route('/follow/user/<int:user_id>/followers', methods=['GET'])
def get_user_followers(user_id):
    """Get a user's followers (public)"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    # Check if profile is public
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile and profile.profile_visibility == 'private':
        return jsonify({'error': 'This profile is private'}), 403
    
    # Eager load follower and profile to avoid N+1
    follows = UserFollow.query.options(
        joinedload(UserFollow.follower).joinedload(User.profile)
    ).filter_by(following_id=user_id)\
        .order_by(UserFollow.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    followers = []
    for f in follows.items:
        user = f.follower
        user_profile = user.profile  # Already loaded via joinedload
        # Only show public profiles
        if user_profile and user_profile.profile_visibility == 'private':
            continue
        followers.append({
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
        })
    
    return jsonify({
        'followers': followers,
        'total': follows.total,
        'page': page,
        'pages': follows.pages,
    })
