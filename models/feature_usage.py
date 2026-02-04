from datetime import datetime
from . import db

# ==========================================================
# USER FEATURE USAGE TRACKING
# Purpose: Track per-user usage of limited features
# For enforcing trial limits (e.g., 5 AI queries/day for Free users)
# ==========================================================

class UserFeatureUsage(db.Model):
    """
    Tracks usage of rate-limited features per user.
    When a user performs an action (e.g., AI query), we increment the counter.
    Resets are handled based on the feature's reset period (daily, monthly, total).
    """
    __tablename__ = 'user_feature_usage'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    feature_key = db.Column(db.String(50), nullable=False)  # e.g., 'ai_queries_limit'
    
    # Usage tracking
    usage_count = db.Column(db.Integer, default=0)
    last_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one record per user per feature
    __table_args__ = (
        db.UniqueConstraint('user_id', 'feature_key', name='unique_user_feature'),
    )
    
    # Relationship
    user = db.relationship('User', backref=db.backref('feature_usage', lazy='dynamic'))
    
    def to_dict(self):
        return {
            'feature_key': self.feature_key,
            'usage_count': self.usage_count,
            'last_reset': self.last_reset.isoformat() if self.last_reset else None
        }
    
    @staticmethod
    def get_or_create(user_id: int, feature_key: str):
        """Get existing usage record or create new one."""
        usage = UserFeatureUsage.query.filter_by(
            user_id=user_id,
            feature_key=feature_key
        ).first()
        
        if not usage:
            usage = UserFeatureUsage(
                user_id=user_id,
                feature_key=feature_key,
                usage_count=0
            )
            db.session.add(usage)
            db.session.commit()
        
        return usage
    
    def should_reset(self, period: str) -> bool:
        """Check if usage counter should be reset based on period."""
        if period == 'total':
            return False  # Never reset for lifetime limits
        
        now = datetime.utcnow()
        
        if period == 'daily':
            # Reset if last reset was on a different day
            return self.last_reset.date() < now.date()
        elif period == 'monthly':
            # Reset if we're in a new month
            return (self.last_reset.year, self.last_reset.month) < (now.year, now.month)
        elif period == 'weekly':
            # Reset if more than 7 days have passed
            return (now - self.last_reset).days >= 7
        
        return False
    
    def reset_if_needed(self, period: str) -> bool:
        """Reset counter if period has elapsed. Returns True if reset occurred."""
        if self.should_reset(period):
            self.usage_count = 0
            self.last_reset = datetime.utcnow()
            db.session.commit()
            return True
        return False
    
    def increment(self) -> int:
        """Increment usage count and return new value."""
        self.usage_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self.usage_count
