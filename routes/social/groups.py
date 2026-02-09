"""
Social API Routes - Discussion Groups
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import uuid
import re
from models import db, User, DiscussionGroup, GroupMember, GroupPost
from routes.decorators import auth_required

groups_bp = Blueprint('groups', __name__)


def slugify(text):
    """Generate URL-safe slug from text"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:100]


@groups_bp.route('/groups', methods=['GET'])
def list_groups():
    """List public groups"""
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = DiscussionGroup.query.filter(
        DiscussionGroup.is_active == True,
        DiscussionGroup.group_type.in_(['public', 'private'])
    )
    
    if category:
        query = query.filter(DiscussionGroup.category == category)
    
    if search:
        query = query.filter(DiscussionGroup.name.ilike(f'%{search}%'))
    
    query = query.order_by(DiscussionGroup.members_count.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'groups': [g.to_dict() for g in pagination.items],
        'total': pagination.total,
        'page': page,
        'pages': pagination.pages,
    })


@groups_bp.route('/groups', methods=['POST'])
@auth_required
def create_group():
    """Create a new group"""
    user = request.user
    data = request.get_json() or {}
    
    if not data.get('name'):
        return jsonify({'error': 'Group name is required'}), 400
    
    slug = slugify(data['name'])
    
    # Check slug uniqueness
    existing = DiscussionGroup.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{uuid.uuid4().hex[:6]}"
    
    group = DiscussionGroup(
        id=str(uuid.uuid4()),
        name=data['name'][:100],
        slug=slug,
        description=data.get('description'),
        group_type=data.get('groupType', 'public') if data.get('groupType') in ['public', 'private', 'invite_only'] else 'public',
        category=data.get('category', 'general') if data.get('category') in ['stocks', 'crypto', 'forex', 'options', 'general'] else 'general',
        owner_id=user.id,
        members_count=1,
    )
    
    db.session.add(group)
    
    # Add creator as owner member
    member = GroupMember(
        group_id=group.id,
        user_id=user.id,
        role='owner'
    )
    db.session.add(member)
    
    db.session.commit()
    
    return jsonify({'success': True, 'group': group.to_dict()}), 201


@groups_bp.route('/groups/<group_id>', methods=['GET'])
def get_group(group_id):
    """Get group details"""
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group or not group.is_active:
        return jsonify({'error': 'Group not found'}), 404
    
    group_data = group.to_dict()
    group_data['owner'] = {
        'id': group.owner.id,
        'name': group.owner.name,
        'avatarUrl': group.owner.avatar_url,
    }
    
    return jsonify({'group': group_data})


@groups_bp.route('/groups/<group_id>/join', methods=['POST'])
@auth_required
def join_group(group_id):
    """Join a group"""
    user = request.user
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group or not group.is_active:
        return jsonify({'error': 'Group not found'}), 404
    
    if group.group_type == 'invite_only':
        return jsonify({'error': 'This group is invite only'}), 403
    
    existing = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
    if existing:
        return jsonify({'error': 'Already a member'}), 400
    
    member = GroupMember(
        group_id=group.id,
        user_id=user.id,
        role='member'
    )
    db.session.add(member)
    group.members_count = (group.members_count or 0) + 1
    db.session.commit()
    
    return jsonify({'success': True})


@groups_bp.route('/groups/<group_id>/leave', methods=['POST'])
@auth_required
def leave_group(group_id):
    """Leave a group"""
    user = request.user
    
    # First lookup group by id or slug
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group:
        return jsonify({'error': 'Group not found'}), 404
    
    member = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
    if not member:
        return jsonify({'error': 'Not a member'}), 400
    
    if member.role == 'owner':
        return jsonify({'error': 'Owner cannot leave. Transfer ownership first.'}), 400
    
    db.session.delete(member)
    if group.members_count:
        group.members_count = max(0, group.members_count - 1)
    db.session.commit()
    
    return jsonify({'success': True})


@groups_bp.route('/groups/<group_id>/posts', methods=['GET'])
def get_group_posts(group_id):
    """Get posts in a group"""
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group or not group.is_active:
        return jsonify({'error': 'Group not found'}), 404
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 50)
    
    posts = GroupPost.query.filter_by(group_id=group.id, is_deleted=False)\
        .order_by(GroupPost.is_pinned.desc(), GroupPost.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for post in posts.items:
        post_data = post.to_dict()
        post_data['author'] = {
            'id': post.user.id,
            'name': post.user.name,
            'avatarUrl': post.user.avatar_url,
        }
        result.append(post_data)
    
    return jsonify({
        'posts': result,
        'total': posts.total,
        'page': page,
        'pages': posts.pages,
    })


@groups_bp.route('/groups/<group_id>/posts', methods=['POST'])
@auth_required
def create_group_post(group_id):
    """Create a post in a group"""
    user = request.user
    
    # First lookup group by id or slug
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group or not group.is_active:
        return jsonify({'error': 'Group not found'}), 404
    
    member = GroupMember.query.filter_by(group_id=group.id, user_id=user.id).first()
    if not member:
        return jsonify({'error': 'Must be a member to post'}), 403
    
    data = request.get_json() or {}
    
    if not data.get('content'):
        return jsonify({'error': 'Content is required'}), 400
    
    post = GroupPost(
        id=str(uuid.uuid4()),
        group_id=group.id,
        user_id=user.id,
        title=data.get('title', '')[:255] if data.get('title') else None,
        content=data['content'],
        post_type=data.get('postType', 'discussion') if data.get('postType') in ['discussion', 'idea', 'poll', 'announcement'] else 'discussion',
    )
    
    db.session.add(post)
    group.posts_count = (group.posts_count or 0) + 1
    db.session.commit()
    
    post_data = post.to_dict()
    post_data['author'] = {
        'id': user.id,
        'name': user.name,
        'avatarUrl': user.avatar_url,
    }
    
    return jsonify({'success': True, 'post': post_data}), 201


@groups_bp.route('/groups/<group_id>/members', methods=['GET'])
def get_group_members(group_id):
    """Get group members"""
    group = DiscussionGroup.query.get(group_id) or \
            DiscussionGroup.query.filter_by(slug=group_id).first()
    
    if not group or not group.is_active:
        return jsonify({'error': 'Group not found'}), 404
    
    members = GroupMember.query.filter_by(group_id=group.id)\
        .order_by(GroupMember.role.asc(), GroupMember.joined_at.asc()).all()
    
    result = []
    for m in members:
        result.append({
            'id': m.user.id,
            'name': m.user.name,
            'avatarUrl': m.user.avatar_url,
            'role': m.role,
            'joinedAt': m.joined_at.isoformat() if m.joined_at else None,
        })
    
    return jsonify({'members': result, 'total': len(result)})


@groups_bp.route('/groups/my', methods=['GET'])
@auth_required
def get_my_groups():
    """Get groups user is a member of"""
    user = request.user
    
    memberships = GroupMember.query.filter_by(user_id=user.id).all()
    
    groups = []
    for m in memberships:
        group_data = m.group.to_dict()
        group_data['myRole'] = m.role
        groups.append(group_data)
    
    return jsonify({'groups': groups})
