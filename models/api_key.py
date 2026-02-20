"""
API Key Models for Developer API Access
"""
from datetime import datetime, timezone
from .base import db

class ApiKey(db.Model):
    """Developer API Keys for accessing /api/v1/... endpoints"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    key_prefix = db.Column(db.String(8), nullable=False)
    key_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'keyPrefix': self.key_prefix,
            'isActive': self.is_active,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastUsedAt': self.last_used_at.isoformat() if self.last_used_at else None,
        }

class ApiUsageLog(db.Model):
    """Logs for API requests made using developer API Keys"""
    __tablename__ = 'api_usage_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    api_key_id = db.Column(db.Integer, db.ForeignKey('api_keys.id'), nullable=False)
    endpoint = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    status_code = db.Column(db.Integer, nullable=False)
    ip_address = db.Column(db.String(45))
    duration_ms = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
