"""
Social & Community Models
PeartoFinance Backend
- User profile extensions, follows, messages, ideas, groups, badges, copy trading
"""
from datetime import datetime, timezone
from .base import db


# =============================================================================
# PHASE 1: USER PROFILE ENHANCEMENTS
# =============================================================================

class UserProfile(db.Model):
    """Extended user profile for social features"""
    __tablename__ = 'user_profiles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    
    # Bio & identity
    bio = db.Column(db.Text)
    public_username = db.Column(db.String(50), unique=True)
    trading_style = db.Column(db.Enum(
        'day_trader', 'swing_trader', 'long_term', 'value', 
        'growth', 'dividend', 'mixed'
    ), default='mixed')
    
    # Visibility settings
    profile_visibility = db.Column(db.Enum('public', 'private', 'anonymous'), default='private')
    show_portfolio = db.Column(db.Boolean, default=False)
    show_performance = db.Column(db.Boolean, default=False)
    show_trades = db.Column(db.Boolean, default=False)
    
    # Stats (denormalized for performance)
    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)
    ideas_count = db.Column(db.Integer, default=0)
    likes_received = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), 
                          onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationship
    user = db.relationship('User', backref=db.backref('profile', uselist=False))
    
    def to_dict(self, include_private=False):
        data = {
            'id': self.id,
            'userId': self.user_id,
            'publicUsername': self.public_username,
            'bio': self.bio,
            'tradingStyle': self.trading_style,
            'profileVisibility': self.profile_visibility,
            'followersCount': self.followers_count,
            'followingCount': self.following_count,
            'ideasCount': self.ideas_count,
            'likesReceived': self.likes_received,
        }
        if include_private:
            data.update({
                'showPortfolio': self.show_portfolio,
                'showPerformance': self.show_performance,
                'showTrades': self.show_trades,
            })
        return data


# =============================================================================
# PHASE 2: SOCIAL CONNECTIONS
# =============================================================================

class UserFollow(db.Model):
    """User follow relationships"""
    __tablename__ = 'user_follows'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('follower_id', 'following_id', name='uq_user_follow'),
        db.Index('idx_follower', 'follower_id'),
        db.Index('idx_following', 'following_id'),
    )
    
    follower = db.relationship('User', foreign_keys=[follower_id], backref='following_rel')
    following = db.relationship('User', foreign_keys=[following_id], backref='followers_rel')


class Conversation(db.Model):
    """User conversations (DMs and groups)"""
    __tablename__ = 'conversations'
    
    id = db.Column(db.String(255), primary_key=True)
    type = db.Column(db.Enum('direct', 'group'), default='direct')
    title = db.Column(db.String(255))
    last_message_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'title': self.title,
            'lastMessageAt': self.last_message_at.isoformat() if self.last_message_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class ConversationParticipant(db.Model):
    """Conversation participants"""
    __tablename__ = 'conversation_participants'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    conversation_id = db.Column(db.String(255), db.ForeignKey('conversations.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_read_at = db.Column(db.DateTime)
    is_muted = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('conversation_id', 'user_id', name='uq_conv_participant'),
    )
    
    conversation = db.relationship('Conversation', backref='participants')
    user = db.relationship('User', backref='conversations')


class Message(db.Model):
    """User-to-user messages"""
    __tablename__ = 'user_messages'  # Named differently from chat_messages (support)
    
    id = db.Column(db.String(255), primary_key=True)
    conversation_id = db.Column(db.String(255), db.ForeignKey('conversations.id'), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.Enum('text', 'image', 'idea_share'), default='text')
    meta_data = db.Column(db.JSON)  # Named meta_data to avoid SQLAlchemy reserved name
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.Index('idx_conv_created', 'conversation_id', 'created_at'),
    )
    
    conversation = db.relationship('Conversation', backref='messages')
    sender = db.relationship('User', backref='sent_messages')
    
    def to_dict(self):
        return {
            'id': self.id,
            'conversationId': self.conversation_id,
            'senderId': self.sender_id,
            'content': self.content,
            'messageType': self.message_type,
            'metadata': self.meta_data,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# PHASE 3: CONTENT & COMMUNITY
# =============================================================================

class TradingIdea(db.Model):
    """User trading ideas/posts"""
    __tablename__ = 'trading_ideas'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20))
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    idea_type = db.Column(db.Enum('long', 'short', 'neutral'), nullable=False)
    target_price = db.Column(db.Numeric(18, 4))
    stop_loss = db.Column(db.Numeric(18, 4))
    entry_price = db.Column(db.Numeric(18, 4))
    timeframe = db.Column(db.Enum('day', 'week', 'month', 'quarter', 'year'))
    status = db.Column(db.Enum('active', 'hit_target', 'stopped_out', 'expired', 'closed'), default='active')
    
    # Engagement stats
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    
    is_public = db.Column(db.Boolean, default=True)
    is_pinned = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.Index('idx_idea_user', 'user_id'),
        db.Index('idx_idea_symbol', 'symbol'),
    )
    
    user = db.relationship('User', backref='trading_ideas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'symbol': self.symbol,
            'title': self.title,
            'content': self.content,
            'ideaType': self.idea_type,
            'targetPrice': float(self.target_price) if self.target_price else None,
            'stopLoss': float(self.stop_loss) if self.stop_loss else None,
            'entryPrice': float(self.entry_price) if self.entry_price else None,
            'timeframe': self.timeframe,
            'status': self.status,
            'viewsCount': self.views_count,
            'likesCount': self.likes_count,
            'commentsCount': self.comments_count,
            'isPublic': self.is_public,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class IdeaLike(db.Model):
    """Likes on trading ideas"""
    __tablename__ = 'idea_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    idea_id = db.Column(db.String(255), db.ForeignKey('trading_ideas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('idea_id', 'user_id', name='uq_idea_like'),
    )


class IdeaComment(db.Model):
    """Comments on trading ideas"""
    __tablename__ = 'idea_comments'
    
    id = db.Column(db.String(255), primary_key=True)
    idea_id = db.Column(db.String(255), db.ForeignKey('trading_ideas.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    parent_id = db.Column(db.String(255), db.ForeignKey('idea_comments.id'))
    content = db.Column(db.Text, nullable=False)
    likes_count = db.Column(db.Integer, default=0)
    is_deleted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship('User', backref='idea_comments')
    idea = db.relationship('TradingIdea', backref='comments')
    replies = db.relationship('IdeaComment', backref=db.backref('parent', remote_side=[id]))
    
    def to_dict(self):
        return {
            'id': self.id,
            'ideaId': self.idea_id,
            'userId': self.user_id,
            'parentId': self.parent_id,
            'content': self.content,
            'likesCount': self.likes_count,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class DiscussionGroup(db.Model):
    """Investment discussion groups"""
    __tablename__ = 'discussion_groups'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True)
    description = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    cover_url = db.Column(db.Text)
    group_type = db.Column(db.Enum('public', 'private', 'invite_only'), default='public')
    category = db.Column(db.Enum('stocks', 'crypto', 'forex', 'options', 'general'), default='general')
    
    # Stats
    members_count = db.Column(db.Integer, default=0)
    posts_count = db.Column(db.Integer, default=0)
    
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    owner = db.relationship('User', backref='owned_groups')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'iconUrl': self.icon_url,
            'coverUrl': self.cover_url,
            'groupType': self.group_type,
            'category': self.category,
            'membersCount': self.members_count,
            'postsCount': self.posts_count,
            'ownerId': self.owner_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class GroupMember(db.Model):
    """Group membership"""
    __tablename__ = 'group_members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    group_id = db.Column(db.String(255), db.ForeignKey('discussion_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.Enum('owner', 'admin', 'moderator', 'member'), default='member')
    joined_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('group_id', 'user_id', name='uq_group_member'),
    )
    
    group = db.relationship('DiscussionGroup', backref='members')
    user = db.relationship('User', backref='group_memberships')


class GroupPost(db.Model):
    """Posts in discussion groups"""
    __tablename__ = 'group_posts'
    
    id = db.Column(db.String(255), primary_key=True)
    group_id = db.Column(db.String(255), db.ForeignKey('discussion_groups.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255))
    content = db.Column(db.Text, nullable=False)
    post_type = db.Column(db.Enum('discussion', 'idea', 'poll', 'announcement'), default='discussion')
    
    likes_count = db.Column(db.Integer, default=0)
    comments_count = db.Column(db.Integer, default=0)
    is_pinned = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    group = db.relationship('DiscussionGroup', backref='posts')
    user = db.relationship('User', backref='group_posts')
    
    def to_dict(self):
        return {
            'id': self.id,
            'groupId': self.group_id,
            'userId': self.user_id,
            'title': self.title,
            'content': self.content,
            'postType': self.post_type,
            'likesCount': self.likes_count,
            'commentsCount': self.comments_count,
            'isPinned': self.is_pinned,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


# =============================================================================
# PHASE 4: GAMIFICATION & ADVANCED FEATURES
# =============================================================================

class Badge(db.Model):
    """Achievement badges"""
    __tablename__ = 'badges'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon_url = db.Column(db.Text)
    category = db.Column(db.Enum('achievement', 'milestone', 'skill', 'community'), nullable=False)
    points = db.Column(db.Integer, default=0)
    criteria = db.Column(db.JSON)  # e.g., {"trades": 10} or {"followers": 100}
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'iconUrl': self.icon_url,
            'category': self.category,
            'points': self.points,
            'criteria': self.criteria,
        }


class UserBadge(db.Model):
    """Badges earned by users"""
    __tablename__ = 'user_badges'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_id = db.Column(db.String(50), db.ForeignKey('badges.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'badge_id', name='uq_user_badge'),
    )
    
    user = db.relationship('User', backref='badges')
    badge = db.relationship('Badge', backref='earned_by')


class CopyTradingLink(db.Model):
    """Copy trading relationships"""
    __tablename__ = 'copy_trading_links'
    
    id = db.Column(db.String(255), primary_key=True)
    leader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    leader_account_id = db.Column(db.String(255), db.ForeignKey('paper_trading_accounts.id'))
    follower_account_id = db.Column(db.String(255), db.ForeignKey('paper_trading_accounts.id'))
    
    allocation_percent = db.Column(db.Numeric(5, 2), default=100)
    max_position_size = db.Column(db.Numeric(18, 2))
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                          onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('leader_id', 'follower_id', name='uq_copy_link'),
    )
    
    leader = db.relationship('User', foreign_keys=[leader_id], backref='copiers')
    follower = db.relationship('User', foreign_keys=[follower_id], backref='copying')
    
    def to_dict(self):
        return {
            'id': self.id,
            'leaderId': self.leader_id,
            'followerId': self.follower_id,
            'allocationPercent': float(self.allocation_percent) if self.allocation_percent else 100,
            'maxPositionSize': float(self.max_position_size) if self.max_position_size else None,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


class CopyTradeExecution(db.Model):
    """Copy trade execution log"""
    __tablename__ = 'copy_trade_executions'
    
    id = db.Column(db.String(255), primary_key=True)
    link_id = db.Column(db.String(255), db.ForeignKey('copy_trading_links.id'), nullable=False)
    leader_transaction_id = db.Column(db.String(255), db.ForeignKey('paper_transactions.id'))
    follower_transaction_id = db.Column(db.String(255), db.ForeignKey('paper_transactions.id'))
    status = db.Column(db.Enum('pending', 'executed', 'failed', 'skipped'), default='pending')
    notes = db.Column(db.Text)
    executed_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    link = db.relationship('CopyTradingLink', backref='executions')
