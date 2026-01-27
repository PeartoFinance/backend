"""
Notification Jobs
Background jobs for watchlist alerts and user notifications
"""
import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


def get_app():
    """Get Flask app instance for context"""
    from app import app
    return app


def check_watchlist_alerts() -> Dict[str, Any]:
    """
    Check all user alerts for price triggers.
    Triggers notifications when target prices are hit.
    Checks both WatchlistItem.target_price and UserAlert model.
    """
    logger.debug("Running watchlist alert check")
    
    try:
        app = get_app()
        with app.app_context():
            from models import db, WatchlistItem, Watchlist, MarketData, UserAlert, User
            
            alerts_sent = 0
            
            # =============================
            # 1. Check UserAlert model (from frontend alerts)
            # =============================
            user_alerts = UserAlert.query.filter_by(
                is_active=True,
                is_triggered=False
            ).all()
            
            for alert in user_alerts:
                market_data = MarketData.query.filter_by(symbol=alert.symbol).first()
                if not market_data or market_data.price is None:
                    continue
                
                current_price = float(market_data.price)
                target_price = float(alert.target_value)
                
                # Check condition
                triggered = False
                if alert.condition == 'above' and current_price >= target_price:
                    triggered = True
                elif alert.condition == 'below' and current_price <= target_price:
                    triggered = True
                
                if triggered:
                    try:
                        from notifications import send_price_alert
                        send_price_alert(
                            user_id=alert.user_id,
                            symbol=alert.symbol,
                            current_price=current_price,
                            target_price=target_price
                        )
                        
                        # Mark as triggered
                        alert.is_triggered = True
                        alert.triggered_at = datetime.utcnow()
                        db.session.commit()
                        
                        alerts_sent += 1
                        logger.info(f"Alert triggered: {alert.symbol} @ ${current_price:.2f} (target: ${target_price:.2f})")
                    except Exception as e:
                        logger.warning(f"Failed to send alert for {alert.symbol}: {e}")
            
            # =============================
            # 2. Check WatchlistItem.target_price (legacy)
            # =============================
            items = WatchlistItem.query.filter(
                WatchlistItem.target_price.isnot(None)
            ).all()
            
            for item in items:
                market_data = MarketData.query.filter_by(symbol=item.symbol).first()
                if not market_data or market_data.price is None:
                    continue
                
                watchlist = Watchlist.query.get(item.watchlist_id)
                if not watchlist:
                    continue
                
                current_price = float(market_data.price)
                target_price = float(item.target_price)
                
                # Check if price is within 1% of target
                if target_price > 0 and abs(current_price - target_price) / target_price < 0.01:
                    try:
                        from notifications import send_price_alert
                        send_price_alert(
                            user_id=watchlist.user_id,
                            symbol=item.symbol,
                            current_price=current_price,
                            target_price=target_price
                        )
                        alerts_sent += 1
                    except Exception as e:
                        logger.warning(f"Failed to send alert for {item.symbol}: {e}")
            
            if alerts_sent > 0:
                logger.info(f"Sent {alerts_sent} watchlist alerts")
            
            return {'status': 'ok', 'alerts_sent': alerts_sent}
    except Exception as e:
        logger.error(f"Watchlist alert check failed: {e}")
        return {'status': 'error', 'error': str(e)}


def send_daily_digest() -> Dict[str, Any]:
    """
    Send daily market digest to subscribed users.
    Includes portfolio summary, watchlist movements, and market highlights.
    """
    logger.info("Starting daily digest job")
    
    try:
        app = get_app()
        with app.app_context():
            from models import db, User, UserWatchlist, MarketData
            from notifications import send_digest_email
            from services.preference_checker import should_send_notification
            
            digests_sent = 0
            skipped = 0
            
            # Get all active users
            users = User.query.filter_by(account_status='active').all()
            
            for user in users:
                try:
                    # Check if user wants daily digest emails
                    if not should_send_notification(user.id, 'daily_digest', 'email'):
                        skipped += 1
                        continue
                    
                    # Get user's watchlist symbols
                    watchlist = UserWatchlist.query.filter_by(user_id=user.id).all()
                    symbols = [w.symbol for w in watchlist]
                    
                    if not symbols:
                        continue
                    
                    # Get market data for watchlist
                    market_data = MarketData.query.filter(
                        MarketData.symbol.in_(symbols)
                    ).all()
                    
                    # Send digest
                    send_digest_email(
                        user_id=user.id,
                        email=user.email,
                        watchlist_data=[m.to_dict() for m in market_data]
                    )
                    digests_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to send digest to user {user.id}: {e}")
            
            logger.info(f"Daily digest complete: {digests_sent} emails sent, {skipped} skipped (preferences)")
            return {'status': 'ok', 'digests_sent': digests_sent, 'skipped': skipped}
    except Exception as e:
        logger.error(f"Daily digest job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def check_earnings_alerts() -> Dict[str, Any]:
    """
    Check for upcoming earnings announcements for watchlist stocks.
    Send reminders to users before earnings release.
    """
    logger.info("Checking earnings alerts")
    
    try:
        app = get_app()
        with app.app_context():
            from models import db, UserWatchlist, EarningsCalendar
            from notifications import send_earnings_reminder
            from datetime import timedelta
            
            alerts_sent = 0
            tomorrow = datetime.utcnow().date() + timedelta(days=1)
            
            # Get earnings happening tomorrow
            earnings = EarningsCalendar.query.filter(
                EarningsCalendar.earnings_date == tomorrow
            ).all()
            
            if not earnings:
                return {'status': 'ok', 'alerts_sent': 0}
            
            earning_symbols = [e.symbol for e in earnings]
            
            # Find users watching these stocks
            watchlist_items = UserWatchlist.query.filter(
                UserWatchlist.symbol.in_(earning_symbols)
            ).all()
            
            # Group by user
            user_earnings = {}
            for item in watchlist_items:
                if item.user_id not in user_earnings:
                    user_earnings[item.user_id] = []
                user_earnings[item.user_id].append(item.symbol)
            
            # Send reminders
            for user_id, symbols in user_earnings.items():
                try:
                    send_earnings_reminder(user_id, symbols)
                    alerts_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to send earnings reminder to user {user_id}: {e}")
            
            logger.info(f"Sent {alerts_sent} earnings reminders")
            return {'status': 'ok', 'alerts_sent': alerts_sent}
    except Exception as e:
        logger.error(f"Earnings alerts check failed: {e}")
        return {'status': 'error', 'error': str(e)}

# ==================== NEWS NOTIFICATIONS ====================
def process_news_notifications() -> Dict[str, Any]:
    """
    Process news notifications for all users
    Fetches recent news and sends to users based on their preferences
    
    Returns:
        Dictionary with job statistics
    """
    logger.info("Starting news notification job")
    start_time = datetime.utcnow()
    
    try:
        app = get_app()
        with app.app_context():
            from handlers.market_data.news_notification_handler import process_news_notifications as fetch_and_send_news
            
            result = fetch_and_send_news()
            
            elapsed_time = (datetime.utcnow() - start_time).total_seconds()
            result['elapsed_seconds'] = elapsed_time
            
            logger.info(f"News notification job completed in {elapsed_time:.2f}s - {result}")
            
            return result
    
    except Exception as e:
        logger.error(f"News notification job failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'elapsed_seconds': (datetime.utcnow() - start_time).total_seconds()
        }