"""
Admin & Vendor Models
PeartoFinance Backend
"""
from datetime import datetime
from .base import db


class Vendor(db.Model):
    """Vendors/Partners"""
    __tablename__ = 'vendors'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    services = db.Column(db.JSON)
    rating = db.Column(db.Numeric(3, 2), default=0.00)
    review_count = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False)
    metadata_json = db.Column('metadata', db.JSON) # metadata is reserved in some contexts, mapping explicitly
    logo_url = db.Column(db.Text)
    website = db.Column(db.String(255))
    status = db.Column(db.Enum('pending', 'active', 'suspended'), default='pending')
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class VendorAPIKey(db.Model):
    """Vendor API keys"""
    __tablename__ = 'vendor_api_keys'
    
    id = db.Column(db.String(255), primary_key=True)
    vendor_id = db.Column(db.String(255), db.ForeignKey('vendors.id'), nullable=False)
    key_name = db.Column(db.String(100))
    api_key = db.Column(db.String(255), unique=True)
    secret_key = db.Column(db.String(255))
    permissions = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime)
    last_used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class VendorCustomAPI(db.Model):
    """Vendor custom API configurations"""
    __tablename__ = 'vendor_custom_apis'
    
    id = db.Column(db.String(255), primary_key=True)
    vendor_id = db.Column(db.String(255), db.ForeignKey('vendors.id'), nullable=False)
    endpoint = db.Column(db.String(255))
    method = db.Column(db.String(10))
    headers = db.Column(db.JSON)
    body_template = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Seller(db.Model):
    """Sellers/Merchants"""
    __tablename__ = 'sellers'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(255))
    description = db.Column(db.Text)
    logo_url = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'suspended'), default='pending')
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    total_sales = db.Column(db.Integer, default=0)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SellerApplication(db.Model):
    """Seller applications"""
    __tablename__ = 'seller_applications'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    business_name = db.Column(db.String(255))
    business_type = db.Column(db.String(100))
    description = db.Column(db.Text)
    documents = db.Column(db.JSON)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    reviewed_by = db.Column(db.Integer)
    reviewed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SellerCategory(db.Model):
    """Seller categories"""
    __tablename__ = 'seller_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)


class Provider(db.Model):
    """Data providers"""
    __tablename__ = 'providers'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(50))
    base_url = db.Column(db.Text)
    api_key = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    rate_limit = db.Column(db.Integer)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class AuditEvent(db.Model):
    """Audit log events"""
    __tablename__ = 'audit_events'
    
    id = db.Column(db.String(255), primary_key=True)
    ts = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    actor = db.Column(db.String(255))
    action = db.Column(db.String(100), nullable=False)
    entity = db.Column(db.String(100))
    entityId = db.Column(db.String(255))
    meta = db.Column(db.Text)
    country_code = db.Column(db.String(10), default='US')


class AnalyticsEvent(db.Model):
    """Analytics events"""
    __tablename__ = 'analytics_events'
    
    id = db.Column(db.String(64), primary_key=True)
    ts = db.Column(db.String(40), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    page = db.Column(db.String(255))
    userId = db.Column(db.String(64))
    sessionId = db.Column(db.String(64))
    meta = db.Column(db.Text)


class NavMetrics(db.Model):
    """Navigation metrics"""
    __tablename__ = 'nav_metrics'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    page = db.Column(db.String(255))
    views = db.Column(db.Integer, default=0)
    unique_views = db.Column(db.Integer, default=0)
    avg_time_seconds = db.Column(db.Integer, default=0)
    bounce_rate = db.Column(db.Numeric(5, 2))
    date = db.Column(db.Date)
    country_code = db.Column(db.String(10))


class AgentRun(db.Model):
    """AI agent runs"""
    __tablename__ = 'agent_runs'
    
    id = db.Column(db.String(255), primary_key=True)
    topic = db.Column(db.Text, nullable=False)
    symbols = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False)
    steps = db.Column(db.Text)
    articleId = db.Column(db.String(255))
    error = db.Column(db.Text)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updatedAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class AIGenerationRun(db.Model):
    """AI content generation runs"""
    __tablename__ = 'ai_generation_runs'
    
    id = db.Column(db.String(255), primary_key=True)
    topic = db.Column(db.Text)
    symbols = db.Column(db.Text)
    articleId = db.Column(db.String(255))
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class AIPostDraft(db.Model):
    """AI post drafts"""
    __tablename__ = 'ai_post_drafts'
    
    id = db.Column(db.String(255), primary_key=True)
    topic = db.Column(db.String(255), nullable=False)
    outline = db.Column(db.Text, nullable=False)
    draft = db.Column(db.Text, nullable=False)
    createdAt = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class Task(db.Model):
    """Admin tasks"""
    __tablename__ = 'tasks'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    assigned_to = db.Column(db.Integer)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed', 'cancelled'), default='pending')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent'), default='medium')
    due_date = db.Column(db.Date)
    created_by = db.Column(db.Integer)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
