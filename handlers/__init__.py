"""
Handlers Package
Contains email service, notification handlers, and other utilities
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

__all__ = [
    'send_welcome_email',
    'send_login_notification_email',
    'send_password_reset_email',
    'send_profile_update_email',
    'send_verification_code_email',
    'send_google_login_email',
    'send_phone_verification_sms',
    'EmailService'
]

