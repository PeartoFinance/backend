"""
Notification Preference Checker
Centralized service to check if a notification should be sent based on user preferences
"""
from typing import Optional
from datetime import datetime, time


def should_send_notification(user_id: int, notification_type: str, channel: str = 'email') -> bool:
    """
    Check if notification should be sent based on user preferences.
    
    Args:
        user_id: The user's ID
        notification_type: Type of notification:
            - security: Login alerts, password changes, new device
            - account: Profile updates, verification status
            - price_alert: Price target hits
            - daily_digest: Daily market summary
            - earnings: Earnings announcements
            - news: Market news
            - marketing: Promotional emails
            - newsletter: Weekly newsletter
        channel: Delivery channel (email, push, sms)
    
    Returns:
        True if notification should be sent, False otherwise
    """
    from models import UserNotificationPref
    
    prefs = UserNotificationPref.query.filter_by(user_id=user_id).first()
    
    # If no preferences set, use defaults based on type
    if not prefs:
        # Security and account notifications default to ON
        if notification_type in ['security', 'account']:
            return True
        # Marketing defaults to OFF
        if notification_type == 'marketing':
            return False
        # Others default to ON for email/push, OFF for sms
        return channel != 'sms'
    
    # Check quiet hours
    if prefs.quiet_hours_enabled and prefs.quiet_hours_start and prefs.quiet_hours_end:
        current_time = datetime.now().time()
        start = prefs.quiet_hours_start
        end = prefs.quiet_hours_end
        
        # Handle overnight quiet hours (e.g., 22:00 to 08:00)
        if start > end:
            in_quiet_hours = current_time >= start or current_time <= end
        else:
            in_quiet_hours = start <= current_time <= end
        
        if in_quiet_hours:
            # During quiet hours, only allow critical security notifications
            if notification_type != 'security':
                return False
    
    # Map notification type + channel to preference field
    pref_map = {
        # Email preferences
        ('security', 'email'): prefs.email_security,
        ('account', 'email'): prefs.email_account,
        ('price_alert', 'email'): prefs.email_price_alerts if prefs.email_price_alerts is not None else prefs.email_alerts,
        ('daily_digest', 'email'): prefs.email_daily_digest,
        ('earnings', 'email'): prefs.email_earnings,
        ('news', 'email'): prefs.email_news,
        ('marketing', 'email'): prefs.email_marketing,
        ('newsletter', 'email'): prefs.email_newsletter,
        # Push preferences
        ('security', 'push'): prefs.push_security,
        ('price_alert', 'push'): prefs.push_price_alerts if prefs.push_price_alerts is not None else prefs.push_alerts,
        ('news', 'push'): prefs.push_news,
        ('earnings', 'push'): prefs.push_earnings,
        # SMS preferences
        ('security', 'sms'): prefs.sms_security,
        ('price_alert', 'sms'): prefs.sms_price_alerts if prefs.sms_price_alerts is not None else prefs.sms_alerts,
    }
    
    key = (notification_type, channel)
    result = pref_map.get(key)
    
    # Default to True for email/push, False for sms if not in map
    if result is None:
        return channel != 'sms'
    
    return bool(result)


def get_default_preferences() -> dict:
    """Return default notification preferences for new users."""
    return {
        'emailSecurity': True,
        'emailAccount': True,
        'emailPriceAlerts': True,
        'emailDailyDigest': True,
        'emailEarnings': True,
        'emailNews': True,
        'emailMarketing': False,
        'emailNewsletter': True,
        'pushSecurity': True,
        'pushPriceAlerts': True,
        'pushNews': True,
        'pushEarnings': True,
        'smsSecurity': False,
        'smsPriceAlerts': False,
        'quietHoursEnabled': False,
        'quietHoursStart': None,
        'quietHoursEnd': None,
    }
