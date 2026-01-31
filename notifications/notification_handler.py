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
    from services.preference_checker import should_send_notification
    
    results = {}
    
    # Map notification type to preference type
    notification_type_map = {
        'price_alert': 'price_alert',
        'welcome': 'account',
        'security': 'security',
        'earnings_reminder': 'earnings',
        'daily_digest': 'daily_digest',
        'news': 'news',
    }
    pref_notification_type = notification_type_map.get(notification_type, 'account')
    
    # Determine which channels to use based on user preferences
    if channels is None:
        channels = []
        if should_send_notification(user_id, pref_notification_type, 'email'):
            channels.append('email')
        if should_send_notification(user_id, pref_notification_type, 'push'):
            channels.append('push')
        if should_send_notification(user_id, pref_notification_type, 'sms'):
            channels.append('sms')
        
        # Default to at least email/push if no channels determined
        if not channels:
            channels = ['email', 'push']
    
    # Send via each channel
    if 'email' in channels:
        try:
            from .email_service import EmailService
            from models import User
            import os
            
            email_service = EmailService()
            user = User.query.get(user_id)
            if user and user.email:
                # Build template data based on notification type
                app_url = os.getenv('APP_URL', 'https://test.pearto.com')
                template_data = {
                    'user_name': user.name or 'User',
                    'app_name': 'Pearto Finance',
                    'dashboard_url': f'{app_url}/dashboard',
                    'security_url': f'{app_url}/profile?tab=devices',
                }
                
                # Merge with provided data
                if data:
                    template_data.update(data)
                
                # Map notification_type to template
                template_map = {
                    'price_alert': 'price_alert',
                    'welcome': 'signup',
                    'security': 'login',
                    'earnings_reminder': 'earnings_reminder',
                    'daily_digest': 'daily_digest',
                }
                
                template_type = template_map.get(notification_type, 'login')
                
                # Add specific fields for price_alert
                if notification_type == 'price_alert' and data:
                    template_data['symbol'] = data.get('symbol', '')
                    template_data['current_price'] = f"{data.get('current_price', 0):.2f}"
                    template_data['target_price'] = f"{data.get('target_price', 0):.2f}"
                    template_data['direction'] = data.get('direction', 'reached')
                
                email_service.send_email(
                    to=user.email,
                    template_type=template_type,
                    data=template_data
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
    from services.preference_checker import should_send_notification
    
    # Double check preference (safety net)
    if not should_send_notification(user_id, 'daily_digest', 'email'):
        return False
        
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


def send_goal_reached_notification(user_id: int, target_amount: float):
    """
    Send celebration notification when a financial goal is reached.
    """
    title = "Financial Goal Reached! 🎉"
    message = f"Incredible news! Your portfolio has hit your target of ${target_amount:,.2f}. You've successfully reached a major financial milestone!"
    
    # We use 'price_alerts' category for user preferences check (logic in should_send_notification)
    return send_notification(
        user_id=user_id,
        notification_type='price_alerts', 
        title=title,
        message=message,
        channels=['email', 'push']
    )


def send_daily_summary(user_id: int, portfolio_val: float, daily_change: float, change_pct: float):
    """
    Send daily P&L summary email/notification.
    """
    direction = "up" if daily_change >= 0 else "down"
    icon = "📈" if daily_change >= 0 else "📉"
    
    title = f"{icon} Daily Portfolio Summary: {direction.title()} ${abs(daily_change):.2f}"
    message = f"Your portfolio ended the day at ${portfolio_val:,.2f}, {direction} ${abs(daily_change):.2f} ({change_pct:+.2f}%)."
    
    # Use 'daily_digest' logic for now or mapped category
    return send_notification(
        user_id=user_id,
        notification_type='daily_digest',
        title=title,
        message=message,
        data={
            'portfolio_val': portfolio_val,
            'daily_change': daily_change,
            'change_pct': change_pct,
            'is_summary': True
        },
        channels=['email', 'push']
    )
