"""
Social API Routes - Trading Ideas
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import uuid
from models import db, User, UserProfile, TradingIdea, IdeaLike, IdeaComment
from routes.decorators import auth_required

ideas_bp = Blueprint('ideas', __name__)


@ideas_bp.route('/social/ideas', methods=['GET'])
def list_ideas():
    """List public trading ideas"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    symbol = request.args.get('symbol')
    idea_type = request.args.get('type')  # long, short, neutral
    status = request.args.get('status', 'active')
    sort_by = request.args.get('sort_by', 'newest')  # newest, popular, comments
    
    query = TradingIdea.query.filter(TradingIdea.is_public == True)
    
    if symbol:
        query = query.filter(TradingIdea.symbol == symbol.upper())
    if idea_type:
        query = query.filter(TradingIdea.idea_type == idea_type)
    if status:
        query = query.filter(TradingIdea.status == status)
    
    # Sort options
    if sort_by == 'popular':
        query = query.order_by(TradingIdea.likes_count.desc())
    elif sort_by == 'comments':
        query = query.order_by(TradingIdea.comments_count.desc())
    elif sort_by == 'views':
        query = query.order_by(TradingIdea.views_count.desc())
    else:  # newest
        query = query.order_by(TradingIdea.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    ideas = []
    for idea in pagination.items:
        idea_data = idea.to_dict()
        user = idea.user
        profile = UserProfile.query.filter_by(user_id=user.id).first()
        idea_data['author'] = {
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
            'verifiedBadge': user.verified_badge,
            'username': profile.public_username if profile else None,
        }
        ideas.append(idea_data)
    
    return jsonify({
        'ideas': ideas,
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
    })


@ideas_bp.route('/social/ideas', methods=['POST'])
@auth_required
def create_idea():
    """Create a new trading idea"""
    user = request.user
    data = request.get_json() or {}
    
    # Validate required fields
    if not data.get('title') or not data.get('content') or not data.get('ideaType'):
        return jsonify({'error': 'Title, content, and idea type are required'}), 400
    
    if data.get('ideaType') not in ['long', 'short', 'neutral']:
        return jsonify({'error': 'Invalid idea type'}), 400
    
    idea = TradingIdea(
        id=str(uuid.uuid4()),
        user_id=user.id,
        symbol=data.get('symbol', '').upper() if data.get('symbol') else None,
        title=data['title'][:255],
        content=data['content'],
        idea_type=data['ideaType'],
        target_price=data.get('targetPrice'),
        stop_loss=data.get('stopLoss'),
        entry_price=data.get('entryPrice'),
        timeframe=data.get('timeframe') if data.get('timeframe') in ['day', 'week', 'month', 'quarter', 'year'] else None,
        is_public=data.get('isPublic', True),
    )
    
    db.session.add(idea)
    
    # Update user's idea count
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if profile:
        profile.ideas_count = (profile.ideas_count or 0) + 1
    
    db.session.commit()
    
    return jsonify({'success': True, 'idea': idea.to_dict()}), 201


@ideas_bp.route('/social/ideas/<idea_id>', methods=['GET'])
def get_idea(idea_id):
    """Get a single trading idea"""
    idea = TradingIdea.query.get(idea_id)
    
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    if not idea.is_public:
        return jsonify({'error': 'This idea is private'}), 403
    
    # Increment view count
    idea.views_count = (idea.views_count or 0) + 1
    db.session.commit()
    
    idea_data = idea.to_dict()
    user = idea.user
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    idea_data['author'] = {
        'id': user.id,
        'name': user.name,
        'avatarUrl': user.avatar_url,
        'verifiedBadge': user.verified_badge,
        'username': profile.public_username if profile else None,
        'tradingStyle': profile.trading_style if profile else None,
    }
    
    return jsonify({'idea': idea_data})


@ideas_bp.route('/social/ideas/<idea_id>', methods=['PUT'])
@auth_required
def update_idea(idea_id):
    """Update a trading idea"""
    user = request.user
    idea = TradingIdea.query.get(idea_id)
    
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    if idea.user_id != user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json() or {}
    
    if 'title' in data:
        idea.title = data['title'][:255]
    if 'content' in data:
        idea.content = data['content']
    if 'status' in data and data['status'] in ['active', 'hit_target', 'stopped_out', 'expired', 'closed']:
        idea.status = data['status']
    if 'targetPrice' in data:
        idea.target_price = data['targetPrice']
    if 'stopLoss' in data:
        idea.stop_loss = data['stopLoss']
    if 'isPublic' in data:
        idea.is_public = bool(data['isPublic'])
    
    db.session.commit()
    
    return jsonify({'success': True, 'idea': idea.to_dict()})


@ideas_bp.route('/social/ideas/<idea_id>', methods=['DELETE'])
@auth_required
def delete_idea(idea_id):
    """Delete a trading idea"""
    user = request.user
    idea = TradingIdea.query.get(idea_id)
    
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    if idea.user_id != user.id:
        return jsonify({'error': 'Not authorized'}), 403
    
    # Delete related likes and comments
    IdeaLike.query.filter_by(idea_id=idea_id).delete()
    IdeaComment.query.filter_by(idea_id=idea_id).delete()
    
    db.session.delete(idea)
    
    # Update user's idea count
    profile = UserProfile.query.filter_by(user_id=user.id).first()
    if profile and profile.ideas_count:
        profile.ideas_count = max(0, profile.ideas_count - 1)
    
    db.session.commit()
    
    return jsonify({'success': True})


@ideas_bp.route('/social/ideas/<idea_id>/like', methods=['POST'])
@auth_required
def like_idea(idea_id):
    """Like a trading idea"""
    user = request.user
    idea = TradingIdea.query.get(idea_id)
    
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    existing = IdeaLike.query.filter_by(idea_id=idea_id, user_id=user.id).first()
    
    if existing:
        # Unlike
        db.session.delete(existing)
        idea.likes_count = max(0, (idea.likes_count or 0) - 1)
        
        # Update author's likes received count
        author_profile = UserProfile.query.filter_by(user_id=idea.user_id).first()
        if author_profile and author_profile.likes_received:
            author_profile.likes_received = max(0, author_profile.likes_received - 1)
        
        db.session.commit()
        return jsonify({'success': True, 'liked': False, 'likesCount': idea.likes_count})
    else:
        # Like
        like = IdeaLike(idea_id=idea_id, user_id=user.id)
        db.session.add(like)
        idea.likes_count = (idea.likes_count or 0) + 1
        
        # Update author's likes received count
        author_profile = UserProfile.query.filter_by(user_id=idea.user_id).first()
        if author_profile:
            author_profile.likes_received = (author_profile.likes_received or 0) + 1
        
        db.session.commit()
        return jsonify({'success': True, 'liked': True, 'likesCount': idea.likes_count})


@ideas_bp.route('/social/ideas/<idea_id>/comments', methods=['GET'])
def get_idea_comments(idea_id):
    """Get comments on an idea"""
    idea = TradingIdea.query.get(idea_id)
    
    if not idea or not idea.is_public:
        return jsonify({'error': 'Idea not found'}), 404
    
    comments = IdeaComment.query.filter_by(idea_id=idea_id, is_deleted=False)\
        .order_by(IdeaComment.created_at.asc()).all()
    
    result = []
    for comment in comments:
        comment_data = comment.to_dict()
        user = comment.user
        comment_data['author'] = {
            'id': user.id,
            'name': user.name,
            'avatarUrl': user.avatar_url,
        }
        result.append(comment_data)
    
    return jsonify({'comments': result})


@ideas_bp.route('/social/ideas/<idea_id>/comments', methods=['POST'])
@auth_required
def add_comment(idea_id):
    """Add a comment to an idea"""
    user = request.user
    idea = TradingIdea.query.get(idea_id)
    
    if not idea:
        return jsonify({'error': 'Idea not found'}), 404
    
    data = request.get_json() or {}
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Content is required'}), 400
    
    comment = IdeaComment(
        id=str(uuid.uuid4()),
        idea_id=idea_id,
        user_id=user.id,
        parent_id=data.get('parentId'),
        content=content,
    )
    
    db.session.add(comment)
    idea.comments_count = (idea.comments_count or 0) + 1
    db.session.commit()
    
    comment_data = comment.to_dict()
    comment_data['author'] = {
        'id': user.id,
        'name': user.name,
        'avatarUrl': user.avatar_url,
    }
    
    return jsonify({'success': True, 'comment': comment_data}), 201


@ideas_bp.route('/social/ideas/my', methods=['GET'])
@auth_required
def get_my_ideas():
    """Get current user's ideas"""
    user = request.user
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    ideas = TradingIdea.query.filter_by(user_id=user.id)\
        .order_by(TradingIdea.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'ideas': [i.to_dict() for i in ideas.items],
        'total': ideas.total,
        'page': page,
        'pages': ideas.pages,
    })
