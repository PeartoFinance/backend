"""
Notification Handler
Unified notification dispatcher for email, push, and in-app notifications
"""
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


def send_notification(
    user_id: int,
    notification_type: str,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    channels: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Send notification through multiple channels based on user preferences.
    
    Args:
        user_id: Target user ID
        notification_type: Type of notification (price_alert, news, earnings, etc.)
        title: Notification title
        message: Notification body
        data: Additional data payload
        channels: Override channels (default: check user preferences)
    
    Returns:
        Dict with status for each channel
    """
    from models import UserNotificationPref
    
    results = {}
    
    # Get user notification preferences
    if channels is None:
        prefs = UserNotificationPref.query.filter_by(user_id=user_id).first()
        if prefs:
            channels = []
            if prefs.email_enabled:
                channels.append('email')
            if prefs.push_enabled:
                channels.append('push')
            if prefs.sms_enabled:
                channels.append('sms')
        else:
            channels = ['email', 'push']  # Default
    
    # Send via each channel
    if 'email' in channels:
        try:
            from .email_service import EmailService
            from models import User
            
            email_service = EmailService()
            user = User.query.get(user_id)
            if user and user.email:
                # Use generic template or custom one based on notification_type
                email_service.send_email(
                    to=user.email,
                    template_type='login',  # Default template, ideally create specific ones
                    data={
                        'user_name': user.name or 'User',
                        'login_time': title,
                        'device_info': message,
                        'ip_address': '-'
                    }
                )
                results['email'] = 'sent'
        except Exception as e:
            logger.error(f"Email notification failed: {e}")
            results['email'] = f'error: {e}'
    
    if 'push' in channels:
        try:
            from .push_service import send_push_notification
            
            result = send_push_notification(
                user_id=user_id,
                title=title,
                message=message,
                data=data
            )
            results['push'] = result.get('status', 'unknown')
        except Exception as e:
            logger.error(f"Push notification failed: {e}")
            results['push'] = f'error: {e}'
    
    return results


def send_price_alert(
    user_id: int,
    symbol: str,
    current_price: float,
    target_price: float
) -> Dict[str, Any]:
    """
    Send price alert notification when stock hits target price.
    """
    direction = "reached" if abs(current_price - target_price) / target_price < 0.01 else (
        "above" if current_price > target_price else "below"
    )
    
    title = f"🎯 {symbol} Price Alert"
    message = f"{symbol} is now ${current_price:.2f}, {direction} your target of ${target_price:.2f}"
    
    return send_notification(
        user_id=user_id,
        notification_type='price_alert',
        title=title,
        message=message,
        data={
            'symbol': symbol,
            'current_price': current_price,
            'target_price': target_price,
            'type': 'price_alert'
        }
    )


def send_digest_email(
    user_id: int,
    email: str,
    watchlist_data: List[Dict[str, Any]]
) -> bool:
    """
    Send daily market digest email.
    """
    try:
        from .email_service import EmailService
        
        email_service = EmailService()
        
        # Build summary
        gainers = [s for s in watchlist_data if s.get('changePercent', 0) > 0]
        losers = [s for s in watchlist_data if s.get('changePercent', 0) < 0]
        
        # Create digest content
        digest_content = f"📈 Gainers: {len(gainers)} | 📉 Losers: {len(losers)}"
        if gainers:
            top_gainer = max(gainers, key=lambda x: x.get('changePercent', 0))
            digest_content += f"\nTop: {top_gainer.get('symbol')} +{top_gainer.get('changePercent', 0):.2f}%"
        
        # Use login template as fallback (ideally create a digest template)
        email_service.send_email(
            to=email,
            template_type='login',
            data={
                'user_name': 'Investor',
                'login_time': digest_content,
                'device_info': 'Daily Market Digest',
                'ip_address': '-'
            }
        )
        return True
    except Exception as e:
        logger.error(f"Digest email failed: {e}")
        return False


def send_earnings_reminder(
    user_id: int,
    symbols: List[str]
) -> Dict[str, Any]:
    """
    Send reminder about upcoming earnings announcements.
    """
    symbols_str = ", ".join(symbols[:5])
    if len(symbols) > 5:
        symbols_str += f" and {len(symbols) - 5} more"
    
    title = "📅 Earnings Tomorrow"
    message = f"Companies on your watchlist reporting tomorrow: {symbols_str}"
    
    return send_notification(
        user_id=user_id,
        notification_type='earnings_reminder',
        title=title,
        message=message,
        data={
            'symbols': symbols,
            'type': 'earnings_reminder'
        }
    )


def send_welcome_notification(user_id: int, name: str) -> Dict[str, Any]:
    """
    Send welcome notification to new users.
    """
    title = "Welcome to PeartoFinance! 🎉"
    message = f"Hi {name}! Start by adding stocks to your watchlist to track prices."
    
    return send_notification(
        user_id=user_id,
        notification_type='welcome',
        title=title,
        message=message
    )


def send_security_alert(
    user_id: int,
    alert_type: str,
    details: str
) -> Dict[str, Any]:
    """
    Send security-related notifications (login from new device, etc.)
    """
    title = "🔒 Security Alert"
    message = f"{details}"
    
    return send_notification(
        user_id=user_id,
        notification_type='security',
        title=title,
        message=message,
        channels=['email', 'push']  # Always send to both channels for security
    )
