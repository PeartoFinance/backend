"""
Miscellaneous Models (FAQs, Glossary, Contact, etc.)
PeartoFinance Backend
"""
from datetime import datetime
from .base import db


class FAQ(db.Model):
    """Frequently asked questions"""
    __tablename__ = 'faqs'
    
    id = db.Column(db.String(50), primary_key=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)
    active = db.Column(db.Boolean, default=True)
    show_on_homepage = db.Column(db.Boolean, default=False)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FAQItem(db.Model):
    """FAQ items (alternative structure)"""
    __tablename__ = 'faq_items'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class GlossaryTerm(db.Model):
    """Financial glossary terms"""
    __tablename__ = 'glossary_terms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    term = db.Column(db.String(100), nullable=False)
    definition = db.Column(db.Text, nullable=False)
    category = db.Column(db.Enum('trading', 'investing', 'derivatives', 'banking', 'crypto', 'economics', 'technical'))
    related_terms = db.Column(db.JSON)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'term': self.term,
            'definition': self.definition,
            'category': self.category,
            'relatedTerms': self.related_terms
        }


class ContactMessage(db.Model):
    """Contact form messages"""
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255))
    email = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('new', 'read', 'replied', 'closed'), default='new')
    replied_by = db.Column(db.Integer)
    replied_at = db.Column(db.DateTime)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Subscriber(db.Model):
    """Newsletter subscribers"""
    __tablename__ = 'subscribers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255))
    is_verified = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    preferences = db.Column(db.JSON)
    source = db.Column(db.String(100))
    country_code = db.Column(db.String(10))
    subscribed_at = db.Column(db.DateTime, default=datetime.utcnow)
    unsubscribed_at = db.Column(db.DateTime)


class Testimonial(db.Model):
    """User testimonials"""
    __tablename__ = 'testimonials'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    company = db.Column(db.String(255))
    avatar_url = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    is_featured = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class TeamMember(db.Model):
    """Team members"""
    __tablename__ = 'team_members'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    bio = db.Column(db.Text)
    photo_url = db.Column(db.Text)
    email = db.Column(db.String(255))
    linkedin = db.Column(db.String(255))
    twitter = db.Column(db.String(255))
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Job(db.Model):
    """Job postings (internal)"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    scheduled_at = db.Column(db.DateTime)
    executed_at = db.Column(db.DateTime)
    result = db.Column(db.Text)
    error = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class JobListing(db.Model):
    """Career job listings"""
    __tablename__ = 'job_listings'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    department = db.Column(db.String(100))
    location = db.Column(db.String(255))
    type = db.Column(db.Enum('full-time', 'part-time', 'contract', 'internship'))
    description = db.Column(db.Text)
    requirements = db.Column(db.Text)
    salary_range = db.Column(db.String(100))
    is_remote = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Affiliate(db.Model):
    """Affiliate links"""
    __tablename__ = 'affiliates'
    
    id = db.Column(db.String(255), primary_key=True)
    providerId = db.Column(db.Text, nullable=False)
    category = db.Column(db.Text, nullable=False)
    affiliateUrl = db.Column(db.Text, nullable=False)
    linkName = db.Column(db.Text)
    calculators = db.Column(db.Text)
    priority = db.Column(db.Integer, default=0)
    updatedAt = db.Column(db.Text, nullable=False)
    active = db.Column(db.Integer, default=1)
    country_code = db.Column(db.String(2))


class MarketingCampaign(db.Model):
    """Marketing campaigns"""
    __tablename__ = 'marketing_campaigns'
    
    id = db.Column(db.String(255), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    type = db.Column(db.String(50))
    status = db.Column(db.Enum('draft', 'active', 'paused', 'completed'), default='draft')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    budget = db.Column(db.Numeric(10, 2))
    target_audience = db.Column(db.JSON)
    metrics = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    """Chat/support messages"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.String(255), primary_key=True)
    conversation_id = db.Column(db.String(255))
    sender_id = db.Column(db.Integer)
    sender_type = db.Column(db.Enum('user', 'agent', 'bot'), default='user')
    message = db.Column(db.Text, nullable=False)
    attachments = db.Column(db.JSON)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Booking(db.Model):
    """Service bookings"""
    __tablename__ = 'bookings'
    
    id = db.Column(db.String(64), primary_key=True)
    country_code = db.Column(db.String(2), default='US')
    name = db.Column(db.String(255))
    firstName = db.Column(db.String(100))
    lastName = db.Column(db.String(100))
    email = db.Column(db.String(255))
    phone = db.Column(db.String(50))
    service = db.Column(db.String(255))
    date = db.Column(db.Date)
    time = db.Column(db.String(20))
    status = db.Column(db.Enum('pending', 'confirmed', 'cancelled', 'completed'), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
