"""
Social API Routes - Private Messaging
PeartoFinance Backend
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import uuid
from models import db, User, UserProfile, Conversation, ConversationParticipant, Message
from routes.decorators import auth_required

messages_bp = Blueprint('messages', __name__)


@messages_bp.route('/messages/conversations', methods=['GET'])
@auth_required
def list_conversations():
    """List user's conversations"""
    user = request.user
    
    participations = ConversationParticipant.query.filter_by(user_id=user.id)\
        .order_by(ConversationParticipant.joined_at.desc()).all()
    
    conversations = []
    for p in participations:
        conv = p.conversation
        # Get other participant(s)
        other_participants = ConversationParticipant.query.filter(
            ConversationParticipant.conversation_id == conv.id,
            ConversationParticipant.user_id != user.id
        ).all()
        
        # Get last message
        last_message = Message.query.filter_by(conversation_id=conv.id)\
            .order_by(Message.created_at.desc()).first()
        
        # Count unread
        unread_count = Message.query.filter(
            Message.conversation_id == conv.id,
            Message.created_at > (p.last_read_at or datetime.min.replace(tzinfo=timezone.utc)),
            Message.sender_id != user.id
        ).count()
        
        conv_data = conv.to_dict()
        conv_data['participants'] = []
        for op in other_participants:
            participant_user = op.user
            conv_data['participants'].append({
                'id': participant_user.id,
                'name': participant_user.name,
                'avatarUrl': participant_user.avatar_url,
            })
        
        if last_message:
            conv_data['lastMessage'] = {
                'content': last_message.content[:100],
                'senderId': last_message.sender_id,
                'createdAt': last_message.created_at.isoformat(),
            }
        
        conv_data['unreadCount'] = unread_count
        conv_data['isMuted'] = p.is_muted
        conversations.append(conv_data)
    
    # Sort by last message
    conversations.sort(key=lambda x: x.get('lastMessageAt') or '', reverse=True)
    
    return jsonify({'conversations': conversations})


@messages_bp.route('/messages/conversations', methods=['POST'])
@auth_required
def start_conversation():
    """Start a new conversation with a user"""
    user = request.user
    data = request.get_json() or {}
    
    recipient_id = data.get('recipientId')
    if not recipient_id:
        return jsonify({'error': 'Recipient ID is required'}), 400
    
    if recipient_id == user.id:
        return jsonify({'error': 'Cannot message yourself'}), 400
    
    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({'error': 'User not found'}), 404
    
    # Check if conversation already exists
    my_convs = ConversationParticipant.query.filter_by(user_id=user.id).all()
    for p in my_convs:
        other = ConversationParticipant.query.filter(
            ConversationParticipant.conversation_id == p.conversation_id,
            ConversationParticipant.user_id == recipient_id
        ).first()
        if other and p.conversation.type == 'direct':
            # Return existing conversation
            return jsonify({
                'conversation': p.conversation.to_dict(),
                'existing': True
            })
    
    # Create new conversation
    conv_id = str(uuid.uuid4())
    conv = Conversation(
        id=conv_id,
        type='direct'
    )
    db.session.add(conv)
    
    # Add participants
    db.session.add(ConversationParticipant(conversation_id=conv_id, user_id=user.id))
    db.session.add(ConversationParticipant(conversation_id=conv_id, user_id=recipient_id))
    
    # Add initial message if provided
    if data.get('message'):
        msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conv_id,
            sender_id=user.id,
            content=data['message']
        )
        db.session.add(msg)
        conv.last_message_at = datetime.now(timezone.utc)
    
    db.session.commit()
    
    return jsonify({
        'conversation': conv.to_dict(),
        'existing': False
    }), 201


@messages_bp.route('/messages/conversations/<conv_id>', methods=['GET'])
@auth_required
def get_conversation_messages(conv_id):
    """Get messages in a conversation"""
    user = request.user
    
    # Verify user is participant
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=user.id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Not authorized'}), 403
    
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 50, type=int), 100)
    
    messages = Message.query.filter_by(conversation_id=conv_id, is_deleted=False)\
        .order_by(Message.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    result = []
    for msg in messages.items:
        msg_data = msg.to_dict()
        msg_data['isMine'] = msg.sender_id == user.id
        if msg.sender:
            msg_data['sender'] = {
                'id': msg.sender.id,
                'name': msg.sender.name,
                'avatarUrl': msg.sender.avatar_url,
            }
        result.append(msg_data)
    
    # Mark as read
    participant.last_read_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({
        'messages': list(reversed(result)),  # Oldest first
        'total': messages.total,
        'page': page,
        'pages': messages.pages,
    })


@messages_bp.route('/messages/conversations/<conv_id>', methods=['POST'])
@auth_required
def send_message(conv_id):
    """Send a message in a conversation"""
    user = request.user
    
    # Verify user is participant
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=user.id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Not authorized'}), 403
    
    data = request.get_json() or {}
    content = data.get('content')
    
    if not content:
        return jsonify({'error': 'Message content is required'}), 400
    
    conv = Conversation.query.get(conv_id)
    
    msg = Message(
        id=str(uuid.uuid4()),
        conversation_id=conv_id,
        sender_id=user.id,
        content=content,
        message_type=data.get('messageType', 'text'),
        meta_data=data.get('metadata'),
    )
    
    db.session.add(msg)
    conv.last_message_at = datetime.now(timezone.utc)
    participant.last_read_at = datetime.now(timezone.utc)
    db.session.commit()
    
    msg_data = msg.to_dict()
    msg_data['isMine'] = True
    msg_data['sender'] = {
        'id': user.id,
        'name': user.name,
        'avatarUrl': user.avatar_url,
    }
    
    return jsonify({'message': msg_data}), 201


@messages_bp.route('/messages/conversations/<conv_id>/read', methods=['PUT'])
@auth_required
def mark_as_read(conv_id):
    """Mark conversation as read"""
    user = request.user
    
    participant = ConversationParticipant.query.filter_by(
        conversation_id=conv_id, user_id=user.id
    ).first()
    
    if not participant:
        return jsonify({'error': 'Not authorized'}), 403
    
    participant.last_read_at = datetime.now(timezone.utc)
    db.session.commit()
    
    return jsonify({'success': True})


@messages_bp.route('/messages/unread-count', methods=['GET'])
@auth_required
def get_unread_count():
    """Get total unread message count"""
    user = request.user
    
    participations = ConversationParticipant.query.filter_by(user_id=user.id).all()
    
    total_unread = 0
    for p in participations:
        if p.is_muted:
            continue
        count = Message.query.filter(
            Message.conversation_id == p.conversation_id,
            Message.created_at > (p.last_read_at or datetime.min.replace(tzinfo=timezone.utc)),
            Message.sender_id != user.id
        ).count()
        total_unread += count
    
    return jsonify({'unreadCount': total_unread})
