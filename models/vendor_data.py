"""
Vendor Data Models
Reviews and Historical Data
"""
from datetime import datetime
from .base import db

class VendorReview(db.Model):
    """User reviews for vendors"""
    __tablename__ = 'vendor_reviews'

    id = db.Column(db.String(255), primary_key=True)
    vendor_id = db.Column(db.String(255), db.ForeignKey('vendors.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) # Assumes User model uses Integer ID based on other files
    rating = db.Column(db.Integer, nullable=False) # 1-5
    comment = db.Column(db.Text)
    is_verified_customer = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='vendor_reviews', lazy=True)
    vendor = db.relationship('Vendor', backref='reviews', lazy=True)

class VendorHistory(db.Model):
    """Historical data points for vendor analysis (charts)"""
    __tablename__ = 'vendor_history'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    vendor_id = db.Column(db.String(255), db.ForeignKey('vendors.id'), nullable=False)
    metric_type = db.Column(db.String(50), nullable=False) # e.g., 'interest_rate_1yr', 'processing_fee'
    value = db.Column(db.Numeric(10, 2), nullable=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow)

    # We might want unique constraint on specific metric per day/time
    # __table_args__ = (db.UniqueConstraint('vendor_id', 'metric_type', 'recorded_at', name='_vendor_metric_uc'),)
    
    vendor = db.relationship('Vendor', backref='history', lazy=True)
