"""
Social API Routes - Badges System
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from models import db, User, UserProfile, Badge, UserBadge
from routes.decorators import auth_required

badges_bp = Blueprint('badges', __name__)


# Predefined badges
DEFAULT_BADGES = [
    {'id': 'first_trade', 'name': 'First Trade', 'description': 'Completed your first trade', 'category': 'milestone', 'points': 10},
    {'id': '10_trades', 'name': 'Active Trader', 'description': 'Completed 10 trades', 'category': 'milestone', 'points': 25},
    {'id': '100_trades', 'name': 'Power Trader', 'description': 'Completed 100 trades', 'category': 'milestone', 'points': 100},
    {'id': 'first_idea', 'name': 'Idea Sharer', 'description': 'Posted your first trading idea', 'category': 'community', 'points': 15},
    {'id': '10_ideas', 'name': 'Thought Leader', 'description': 'Posted 10 trading ideas', 'category': 'community', 'points': 50},
    {'id': '10_followers', 'name': 'Rising Star', 'description': 'Gained 10 followers', 'category': 'community', 'points': 25},
    {'id': '100_followers', 'name': 'Influencer', 'description': 'Gained 100 followers', 'category': 'community', 'points': 100},
    {'id': 'verified', 'name': 'Verified Investor', 'description': 'Completed identity verification', 'category': 'achievement', 'points': 50},
    {'id': 'profitable_week', 'name': 'Weekly Winner', 'description': 'Had a profitable trading week', 'category': 'achievement', 'points': 20},
    {'id': 'profitable_month', 'name': 'Monthly Champion', 'description': 'Had a profitable trading month', 'category': 'achievement', 'points': 50},
    {'id': 'diversified', 'name': 'Diversifier', 'description': 'Hold 10+ different assets', 'category': 'skill', 'points': 30},
    {'id': 'early_adopter', 'name': 'Early Adopter', 'description': 'Joined in the first year', 'category': 'achievement', 'points': 100},
]


@badges_bp.route('/social/badges', methods=['GET'])
def list_all_badges():
    """List all available badges"""
    badges = Badge.query.filter_by(is_active=True).order_by(Badge.sort_order).all()
    return jsonify({'badges': [b.to_dict() for b in badges]})


@badges_bp.route('/social/badges/my', methods=['GET'])
@auth_required
def get_my_badges():
    """Get current user's earned badges"""
    user = request.user
    
    user_badges = UserBadge.query.filter_by(user_id=user.id)\
        .order_by(UserBadge.earned_at.desc()).all()
    
    result = []
    for ub in user_badges:
        badge_data = ub.badge.to_dict()
        badge_data['earnedAt'] = ub.earned_at.isoformat() if ub.earned_at else None
        result.append(badge_data)
    
    # Get total points
    total_points = sum(b.badge.points or 0 for b in user_badges)
    
    return jsonify({
        'badges': result,
        'totalPoints': total_points,
        'badgeCount': len(result)
    })


@badges_bp.route('/social/badges/user/<int:user_id>', methods=['GET'])
def get_user_badges(user_id):
    """Get a user's badges"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if profile is public
    profile = UserProfile.query.filter_by(user_id=user_id).first()
    if profile and profile.profile_visibility == 'private':
        return jsonify({'error': 'This profile is private'}), 403
    
    user_badges = UserBadge.query.filter_by(user_id=user_id)\
        .order_by(UserBadge.earned_at.desc()).all()
    
    result = []
    for ub in user_badges:
        badge_data = ub.badge.to_dict()
        badge_data['earnedAt'] = ub.earned_at.isoformat() if ub.earned_at else None
        result.append(badge_data)
    
    return jsonify({'badges': result, 'badgeCount': len(result)})


@badges_bp.route('/social/badges/seed', methods=['POST'])
def seed_badges():
    """Seed default badges (admin only)"""
    # Simple check - in production use proper admin auth
    if request.headers.get('X-Admin-Secret') != 'pearto-admin-2024':
        return jsonify({'error': 'Unauthorized'}), 401
    
    created = 0
    for badge_data in DEFAULT_BADGES:
        existing = Badge.query.get(badge_data['id'])
        if not existing:
            badge = Badge(
                id=badge_data['id'],
                name=badge_data['name'],
                description=badge_data['description'],
                category=badge_data['category'],
                points=badge_data['points'],
            )
            db.session.add(badge)
            created += 1
    
    db.session.commit()
    
    return jsonify({'success': True, 'created': created})


@badges_bp.route('/social/badges/award/<badge_id>', methods=['POST'])
@auth_required
def check_and_award_badge(badge_id):
    """Check if user qualifies for badge and award it"""
    user = request.user
    
    badge = Badge.query.get(badge_id)
    if not badge or not badge.is_active:
        return jsonify({'error': 'Badge not found'}), 404
    
    # Check if already earned
    existing = UserBadge.query.filter_by(user_id=user.id, badge_id=badge_id).first()
    if existing:
        return jsonify({'error': 'Badge already earned', 'alreadyEarned': True})
    
    # Award badge
    user_badge = UserBadge(user_id=user.id, badge_id=badge_id)
    db.session.add(user_badge)
    
    # Update user's total points
    user.total_reward_points = (user.total_reward_points or 0) + (badge.points or 0)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'badge': badge.to_dict(),
        'totalPoints': user.total_reward_points
    })


@badges_bp.route('/social/badges/leaderboard', methods=['GET'])
def get_leaderboard():
    """Get badge points leaderboard"""
    limit = min(request.args.get('limit', 10, type=int), 50)
    
    users = User.query.filter(User.total_reward_points > 0)\
        .order_by(User.total_reward_points.desc())\
        .limit(limit).all()
    
    leaderboard = []
    for i, user in enumerate(users, 1):
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        if profile and profile.profile_visibility == 'private':
            continue
        leaderboard.append({
            'rank': i,
            'userId': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'points': user.total_reward_points,
            'verifiedBadge': user.verified_badge,
        })
    
    return jsonify({'leaderboard': leaderboard})
