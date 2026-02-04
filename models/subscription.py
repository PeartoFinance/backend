from datetime import datetime
from . import db
from sqlalchemy.dialects.mysql import JSON

# ==========================================================
# SUBSCRIPTION SYSTEM MODELS
# This file contains all tables related to the SaaS/Subscription feature.
# It is kept separate from 'user.py' or 'portfolio.py' to ensure
# the subscription system is a modular, isolated component.
# ==========================================================

class SubscriptionPlan(db.Model):
    """
    Represents the Products/Plans available for purchase (e.g., 'Pro', 'Enterprise').
    
    DESIGN CHOICE:
    We use a JSON column for 'features' instead of creating separate tables for every feature.
    Why? This allows the Admin to add new features (e.g., "AI Analysis") instantly
    without needing a developer to change the database schema.
    """
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)  # Example: "Pro Plan"
    description = db.Column(db.Text, nullable=True)   # Displayed on the pricing card
    
    # Financial Details
    price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')     # ISO Code (USD, INR, EUR)
    interval = db.Column(db.String(20), default='monthly') # Options: 'monthly', 'yearly', 'lifetime'
    duration_days = db.Column(db.Integer, default=30)     # Used to calculate expiry dates automatically
    
    # FEATURE GATING (The Core Logic)
    # Stores flags like: {"daily_emails": true, "max_watchlists": 10}
    features = db.Column(JSON, nullable=True)
    
    # Scaling Options (Future Proofing)
    max_members = db.Column(db.Integer, default=1)        # 1 = Personal, >1 = Team Plan
    is_active = db.Column(db.Boolean, default=True)       # If False, plan is hidden from new users
    is_featured = db.Column(db.Boolean, default=False)    # If True, highlighted as "Best Value" on UI
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert object to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'currency': self.currency,
            'interval': self.interval,
            'features': self.features,
            'maxMembers': self.max_members,
            'description': self.description,
            'isFeatured': self.is_featured
        }


class SubscriptionCoupon(db.Model):
    """
    Represents Marketing Discounts (e.g., 'DIWALI2026').
    
    DESIGN CHOICE:
    Supports both 'percent' and 'fixed' logic to handle different types of sales.
    Dates are strictly enforced to allow temporary automated campaigns.
    """
    __tablename__ = 'subscription_coupons'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)  # The code user types (Case Insensitive)
    
    # Discount Architecture
    discount_type = db.Column(db.String(20), default='percent')   # 'percent' (20% off) or 'fixed' ($20 off)
    discount_value = db.Column(db.Numeric(10, 2), nullable=False) # The numeric value (20.00)
    
    # Constraints
    valid_from = db.Column(db.DateTime, default=datetime.utcnow)
    valid_until = db.Column(db.DateTime, nullable=True)           # If null, never expires
    max_redemptions = db.Column(db.Integer, nullable=True)        # Example: "First 100 users only"
    times_redeemed = db.Column(db.Integer, default=0)             # Audit counter
    is_active = db.Column(db.Boolean, default=True)               # Kill switch for Admin
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class UserSubscription(db.Model):
    """
    Links a User to a Plan. This is the 'Source of Truth' for access rights.
    
    DESIGN CHOICE:
    This table explicitly defines the relationship between the Payment Gateway 
    and the Permission System. It stores external IDs so we can track renewals.
    """
    __tablename__ = 'user_subscriptions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    plan_id = db.Column(db.Integer, db.ForeignKey('subscription_plans.id'), nullable=False)
    
    # Status Management
    # 'active' = User can access features
    # 'cancelled' = User cancelled, but might still have days left
    # 'expired' = Access revoked
    status = db.Column(db.String(20), default='active')
    auto_renew = db.Column(db.Boolean, default=True)
    
    # Timestamps for Access Control
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    current_period_end = db.Column(db.DateTime, nullable=False)   # CRITICAL: Access ends after this date
    cancelled_at = db.Column(db.DateTime, nullable=True)
    
    # PAYMENT INDEPENDENCE
    # We store WHICH gateway was used (paypal/stripe) and the external ID.
    # This allows us to have some users on PayPal and some on Stripe simultaneously.
    payment_gateway = db.Column(db.String(50), nullable=True)     # e.g., 'paypal', 'stripe'
    external_subscription_id = db.Column(db.String(100), nullable=True) # The ID from the gateway
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('subscription', uselist=False))
    plan = db.relationship('SubscriptionPlan')


class PaymentTransaction(db.Model):
    """
    An immutable Audit Log of all financial movements.
    Used for Admin Dashboard reporting and Tax/Accounting.
    """
    __tablename__ = 'payment_transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey('user_subscriptions.id'), nullable=True)
    
    # Amount Details
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='USD')
    
    # Transaction State
    status = db.Column(db.String(20), nullable=False) # 'succeeded', 'failed', 'refunded'
    
    # Gateway Meta Data
    gateway = db.Column(db.String(50), nullable=False)
    gateway_transaction_id = db.Column(db.String(100), nullable=True) # Reference for resolving disputes
    description = db.Column(db.String(255), nullable=True)            # e.g., "Pro Plan - Nov Renewal"
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
