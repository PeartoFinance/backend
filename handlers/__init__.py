"""
Handlers Package
Contains email service, notification handlers, activity tracking, and other utilities
"""
from .email_service import (
    send_welcome_email,
    send_login_notification_email,
    send_password_reset_email,
    send_profile_update_email,
    send_verification_code_email,
    send_google_login_email,
    send_phone_verification_sms,
    EmailService
)

from .activity_handler import (
    track_activity,
    track_login,
    track_signup,
    track_logout,
    track_document_upload,
    track_alert_created,
    track_alert_triggered,
    track_watchlist_add,
    track_watchlist_remove,
    track_course_enroll,
    track_course_unenroll,
    track_module_complete,
    track_profile_update,
    track_password_change,
    track_settings_update,
    track_portfolio_transaction,
)

__all__ = [
    # Email
    'send_welcome_email',
    'send_login_notification_email',
    'send_password_reset_email',
    'send_profile_update_email',
    'send_verification_code_email',
    'send_google_login_email',
    'send_phone_verification_sms',
    'EmailService',
    # Activity
    'track_activity',
    'track_login',
    'track_signup',
    'track_logout',
    'track_document_upload',
    'track_alert_created',
    'track_alert_triggered',
    'track_watchlist_add',
    'track_watchlist_remove',
    'track_course_enroll',
    'track_course_unenroll',
    'track_module_complete',
    'track_profile_update',
    'track_password_change',
    'track_settings_update',
    'track_portfolio_transaction',
]
