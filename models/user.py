"""
User-related Database Models
PeartoFinance Backend
"""
from datetime import datetime, timezone
from .base import db


class User(db.Model):
    """User accounts table - matches SQL schema exactly"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255))
    role = db.Column(db.String(50), nullable=False, default='user')
    active = db.Column(db.SmallInteger, default=1)
    createdAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updatedAt = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    forceReset = db.Column(db.SmallInteger, default=0)
    firebase_uid = db.Column(db.String(255))
    avatar_url = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_login_at = db.Column(db.DateTime)
    account_status = db.Column(db.Enum('active', 'deactivated', 'suspended', 'deleted'), default='active')
    deactivated_at = db.Column(db.DateTime)
    deactivation_reason = db.Column(db.Text)
    referred_by = db.Column(db.Integer)
    referral_code = db.Column(db.String(50), unique=True)
    total_reward_points = db.Column(db.Integer, default=0)
    email_verified = db.Column(db.Boolean, default=False)
    email_verified_at = db.Column(db.DateTime)
    phone_verified = db.Column(db.Boolean, default=False)
    phone_verified_at = db.Column(db.DateTime)
    id_verified = db.Column(db.Boolean, default=False)
    id_verified_at = db.Column(db.DateTime)
    verified_badge = db.Column(db.Boolean, default=False)
    phone = db.Column(db.String(20))
    currency = db.Column(db.String(3), default='USD')
    tax_residency = db.Column(db.String(100))
    language_pref = db.Column(db.String(10), default='en')
    country_code = db.Column(db.String(2), default='US')
    # Profile customization fields
    specializations = db.Column(db.JSON)  # [{"id": "1", "name": "Equities", "selected": true}, ...]
    certifications = db.Column(db.JSON)   # [{"id": "1", "name": "CFA Level I", "level": true}, ...]
    hourly_rate = db.Column(db.Numeric(10, 2))

    # Relationships
    notification_preferences = db.relationship('UserNotificationPref', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'avatarUrl': self.avatar_url,
            'phone': self.phone,
            'countryCode': self.country_code,
            'currency': self.currency,
            'languagePref': self.language_pref,
            'emailVerified': self.email_verified,
            'phoneVerified': self.phone_verified,
            'idVerified': self.id_verified,
            'verifiedBadge': self.verified_badge,
            'accountStatus': self.account_status,
            'totalRewardPoints': self.total_reward_points,
            'referralCode': self.referral_code,
            'referredBy': self.referred_by,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'lastLoginAt': self.last_login_at.isoformat() if self.last_login_at else None,
            'hasPassword': bool(self.password),
            'specializations': self.specializations or [],
            'certifications': self.certifications or [],
            'hourlyRate': float(self.hourly_rate) if self.hourly_rate else None,
        }


class PasswordResetToken(db.Model):
    """Password reset tokens"""
    __tablename__ = 'password_reset_tokens'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.String(255), nullable=False, unique=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserSession(db.Model):
    """User login sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    token = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserDevice(db.Model):
    """User registered devices"""
    __tablename__ = 'user_devices'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    device_type = db.Column(db.String(50))
    device_name = db.Column(db.String(255))
    device_token = db.Column(db.Text)
    platform = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserActivity(db.Model):
    """User activity tracking"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(100), nullable=False)
    entity_type = db.Column(db.String(50))
    entity_id = db.Column(db.String(255))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserAlert(db.Model):
    """User price/event alerts"""
    __tablename__ = 'user_alerts'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symbol = db.Column(db.String(20))
    alert_type = db.Column(db.String(50))
    condition = db.Column(db.String(50))
    target_value = db.Column(db.Numeric(18, 4))
    is_triggered = db.Column(db.Boolean, default=False)
    triggered_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    notify_email = db.Column(db.Boolean, default=True)
    notify_push = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserNotificationPref(db.Model):
    """User notification preferences - granular control over all notification types"""
    __tablename__ = 'user_notification_prefs'
     
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Legacy fields (kept for backward compatibility)
    email_marketing = db.Column(db.Boolean, default=False)
    email_alerts = db.Column(db.Boolean, default=True)
    email_news = db.Column(db.Boolean, default=True)
    push_alerts = db.Column(db.Boolean, default=True)
    push_news = db.Column(db.Boolean, default=True)
    sms_alerts = db.Column(db.Boolean, default=False)
    
    # Security & Account notifications (always recommended ON)
    email_security = db.Column(db.Boolean, default=True)  # Login alerts, password changes
    email_account = db.Column(db.Boolean, default=True)   # Account updates, profile changes
    
    # Trading & Market notifications
    email_price_alerts = db.Column(db.Boolean, default=True)   # Price target hits
    email_daily_digest = db.Column(db.Boolean, default=True)   # Daily market summary
    email_portfolio_summary = db.Column(db.Boolean, default=True) # Daily P&L summary
    email_earnings = db.Column(db.Boolean, default=True)       # Earnings reminders
    email_newsletter = db.Column(db.Boolean, default=True)     # Weekly newsletter
    
    # Push notifications
    push_security = db.Column(db.Boolean, default=True)
    push_price_alerts = db.Column(db.Boolean, default=True)
    push_earnings = db.Column(db.Boolean, default=True)
    
    # SMS (premium)
    sms_security = db.Column(db.Boolean, default=False)
    sms_price_alerts = db.Column(db.Boolean, default=False)
    
    # Quiet hours (do not disturb)
    quiet_hours_enabled = db.Column(db.Boolean, default=False)
    quiet_hours_start = db.Column(db.Time)  # e.g., 22:00
    quiet_hours_end = db.Column(db.Time)    # e.g., 08:00
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        db.UniqueConstraint('user_id', name='ux_user_notification_prefs_user_id'),
    )
    def to_dict(self):
        return {
            # Email preferences
            'emailSecurity': self.email_security if self.email_security is not None else True,
            'emailAccount': self.email_account if self.email_account is not None else True,
            'emailPriceAlerts': self.email_price_alerts if self.email_price_alerts is not None else self.email_alerts,
            'emailDailyDigest': self.email_daily_digest if self.email_daily_digest is not None else True,
            'emailPortfolioSummary': self.email_portfolio_summary if self.email_portfolio_summary is not None else True,
            'emailEarnings': self.email_earnings if self.email_earnings is not None else True,
            'emailNews': self.email_news if self.email_news is not None else True,
            'emailMarketing': self.email_marketing if self.email_marketing is not None else False,
            'emailNewsletter': self.email_newsletter if self.email_newsletter is not None else True,
            # Push preferences
            'pushSecurity': self.push_security if self.push_security is not None else True,
            'pushPriceAlerts': self.push_price_alerts if self.push_price_alerts is not None else self.push_alerts,
            'pushNews': self.push_news if self.push_news is not None else True,
            'pushEarnings': self.push_earnings if self.push_earnings is not None else True,
            # SMS preferences
            'smsSecurity': self.sms_security if self.sms_security is not None else False,
            'smsPriceAlerts': self.sms_price_alerts if self.sms_price_alerts is not None else self.sms_alerts,
            # Quiet hours
            'quietHoursEnabled': self.quiet_hours_enabled if self.quiet_hours_enabled is not None else False,
            'quietHoursStart': self.quiet_hours_start.strftime('%H:%M') if self.quiet_hours_start else None,
            'quietHoursEnd': self.quiet_hours_end.strftime('%H:%M') if self.quiet_hours_end else None,
        }
    

# ============== user news preference table =================
class NewsPreference(db.Model):
    __tablename__ = 'news_preferences'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    companies = db.Column(db.JSON)     # ["AAPL", "TSLA"]
    categories = db.Column(db.JSON)    # ["finance", "tech"]
    news_type = db.Column(db.Enum('company', 'independent'), nullable=False)

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


# To make Cron safe and idempotent.
class NewsNotification(db.Model):
        __tablename__ = 'news_notifications'

        id = db.Column(db.Integer, primary_key=True)
        user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
        news_id = db.Column(db.Integer, nullable=False)

        sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

        __table_args__ = (
            db.UniqueConstraint('user_id', 'news_id', name='ux_user_news_notification'),
        )


# ===================

#  User financial goals models
class FinancialGoalNotification(db.Model):
    """
    Tracks sent notifications for financial goal achievements
    (cron-safe, idempotent)
    """
    __tablename__ = 'financial_goal_notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False
    )

    goal_id = db.Column(
        db.Integer,
        db.ForeignKey('financial_goals.id'),
        nullable=False
    )

    sent_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        db.UniqueConstraint(
            'user_id',
            'goal_id',
            name='ux_user_financial_goal_notification'
        ),
    )

#  =====================
class DailySummaryNotification(db.Model):
    """
    Tracks sent daily P&L summaries to prevent duplicate emails per day.
    """
    __tablename__ = 'daily_summary_notifications'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False) # The date this summary covers
    sent_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'date', name='ux_user_daily_summary_date'),
    )


class UserDashboardConfig(db.Model):
    """User dashboard widget configuration"""
    __tablename__ = 'user_dashboard_config'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    layout = db.Column(db.JSON)
    widgets = db.Column(db.JSON)
    theme = db.Column(db.String(50), default='dark')
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


class UserDocument(db.Model):
    """User uploaded documents for verification"""
    __tablename__ = 'user_documents'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_type = db.Column(db.String(50))
    file_url = db.Column(db.Text)
    status = db.Column(db.Enum('pending', 'approved', 'rejected'), default='pending')
    reviewed_by = db.Column(db.Integer)
    reviewed_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserSavedTerm(db.Model):
    """User saved glossary terms"""
    __tablename__ = 'user_saved_terms'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    term_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class UserEconomicEvent(db.Model):
    """User subscribed economic events"""
    __tablename__ = 'user_economic_events'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    event_id = db.Column(db.String(255), nullable=False)
    notify_before = db.Column(db.Integer, default=30)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class LoginEvent(db.Model):
    """Login history/events"""
    __tablename__ = 'login_events'
    
    id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_type = db.Column(db.String(50))
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    location = db.Column(db.String(255))
    success = db.Column(db.Boolean, default=True)
    failure_reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Role(db.Model):
    """Admin roles with granular permissions"""
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    permissions = db.Column(db.JSON)  # {"dashboard": true, "users": true, ...}
    is_system = db.Column(db.Boolean, default=False)  # System roles can't be deleted
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # All available permission keys (matching sidebar sections)
    PERMISSION_KEYS = [
        'dashboard',
        'content',
        'team_manage',       # Granular
        'blog_manage',       # Granular
        'educational',
        'courses_manage',    # Granular
        'instructors_manage', # Granular
        'news_media',
        'radio_manage',      # Granular
        'tv_manage',         # Granular
        'news_import',       # Granular
        'live_sports',       # Granular
        'sports_config',     # Granular
        'events_jobs',
        'help_center',
        'users_access',
        'users_view',        # Granular
        'roles_management',  # Granular
        'subscriptions_view', # Granular
        'bookings',
        'business',
        'products_manage',   # Granular
        'orders_manage',     # Granular
        'vendors_manage',    # Granular
        'sellers_manage',    # Granular
        'seller_applications', # Granular
        'financial',
        'transactions_view', # Granular
        'deposits_manage',   # Granular
        'withdrawals_manage', # Granular
        'market_data',
        'business_profiles',
        'marketing',
        'communications',
        'ai_features',
        'ai_agent',          # Granular
        'ai_content_writer', # Granular
        'chart_analysis',    # Granular
        'system',
        'system_tools',      # Granular
        'system_tasks',      # Granular
        'system_scheduler',  # Granular
        'system_audit',      # Granular
        'apis_integration',
        'configuration',
    ]
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': self.permissions or {},
            'isSystem': self.is_system,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    @staticmethod
    def get_superadmin_permissions():
        """Returns all permissions enabled (for superadmin)"""
        return {key: True for key in Role.PERMISSION_KEYS}
    
    @staticmethod
    def get_default_admin_permissions():
        """Returns default admin permissions (no roles management)"""
        perms = {key: True for key in Role.PERMISSION_KEYS}
        perms['roles_management'] = False
        return perms


class AdminUser(db.Model):
    """Links users to admin roles (separate from basic user.role field)"""
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='admin_profile')
    role = db.relationship('Role', backref='admin_users')
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'roleId': self.role_id,
            'isSuperadmin': self.is_superadmin,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'user': self.user.to_dict() if self.user else None,
            'role': self.role.to_dict() if self.role else None,
        }
    
    def get_permissions(self):
        """Get effective permissions for this admin"""
        if self.is_superadmin:
            return Role.get_superadmin_permissions()
        return self.role.permissions if self.role else {}

