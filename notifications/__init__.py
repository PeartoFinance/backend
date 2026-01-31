"""
Notifications Package
Unified notification services for email, push, and in-app notifications
"""

from .notification_handler import (
    send_notification,
    send_price_alert,
    send_digest_email,
    send_earnings_reminder,
    send_goal_reached_notification,
    send_daily_summary,
)
from .push_service import (
    send_push_notification,
    send_bulk_push,
    register_device,
)
# Email service uses class-based EmailService
from .email_service import (
    EmailService,
    send_welcome_email,
    send_login_notification_email,
    send_password_reset_email,
)

__all__ = [
    'send_notification',
    'send_price_alert',
    'send_digest_email',
    'send_earnings_reminder',
    'send_goal_reached_notification',
    'send_daily_summary',
    'send_push_notification',
    'send_bulk_push',
    'register_device',
    'EmailService',
    'send_welcome_email',
    'send_login_notification_email',
    'send_password_reset_email',
]
