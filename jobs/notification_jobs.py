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
    from models import db
    
    logger.debug("Running watchlist alert check")
    
    try:
        app = get_app()
        with app.app_context():
            from models import WatchlistItem, Watchlist, MarketData, UserAlert, User
            
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
    finally:
        try:
            db.session.remove()
        except:
            pass


def send_daily_digest() -> Dict[str, Any]:
    """
    Send daily market digest to subscribed users.
    Includes portfolio summary, watchlist movements, and market highlights.
    """
    from models import db
    
    logger.info("Starting daily digest job")
    
    try:
        app = get_app()
        with app.app_context():
            from models import User, UserWatchlist, MarketData
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
    finally:
        try:
            db.session.remove()
        except:
            pass


def check_earnings_alerts() -> Dict[str, Any]:
    """
    Check for upcoming earnings announcements for both watchlist stocks AND portfolio holdings.
    Send reminders to users before earnings release.
    """
    from models import db
    
    logger.info("Checking earnings alerts for holdings and watchlists")
    
    try:
        app = get_app()
        with app.app_context():
            from models import UserWatchlist, PortfolioHolding, UserPortfolio, EarningsCalendar
            from notifications import send_earnings_reminder
            from datetime import timedelta
            
            alerts_sent = 0
            tomorrow = datetime.utcnow().date() + timedelta(days=1)
            
            # 1. Get symbols reporting earnings tomorrow
            earnings = EarningsCalendar.query.filter(
                EarningsCalendar.earnings_date == tomorrow
            ).all()
            
            if not earnings:
                return {'status': 'ok', 'alerts_sent': 0, 'message': 'No earnings tomorrow'}
            
            report_symbols = [e.symbol for e in earnings]
            
            # Dictionary to store unique symbols per user {user_id: set(symbols)}
            user_symbols_map = {}

            # 2. Check Watchlists
            watchlist_items = UserWatchlist.query.filter(
                UserWatchlist.symbol.in_(report_symbols)
            ).all()
            for item in watchlist_items:
                if item.user_id not in user_symbols_map:
                    user_symbols_map[item.user_id] = set()
                user_symbols_map[item.user_id].add(item.symbol)

            # 3. Check Portfolio Holdings (NEW)
            # Find users who actually OWN these stocks
            holdings = PortfolioHolding.query.join(UserPortfolio).filter(
                PortfolioHolding.symbol.in_(report_symbols)
            ).all()
            for h in holdings:
                user_id = h.portfolio.user_id # Access via relationship
                if user_id not in user_symbols_map:
                    user_symbols_map[user_id] = set()
                user_symbols_map[user_id].add(h.symbol)
            
            # 4. Send uniquely grouped reminders
            for user_id, symbols_set in user_symbols_map.items():
                try:
                    symbols_list = list(symbols_set)
                    send_earnings_reminder(user_id, symbols_list)
                    alerts_sent += 1
                except Exception as e:
                    logger.warning(f"Failed to send earnings reminder to user {user_id}: {e}")
            
            logger.info(f"Sent {alerts_sent} earnings reminders (Holdings + Watchlist)")
            return {'status': 'ok', 'alerts_sent': alerts_sent}
    except Exception as e:
        logger.error(f"Earnings alerts check failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass

# ==================== NEWS NOTIFICATIONS ====================
def process_news_notifications() -> Dict[str, Any]:
    """
    Process news notifications for all users
    Fetches recent news and sends to users based on their preferences
    
    Returns:
        Dictionary with job statistics
    """
    from models import db
    
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
    finally:
        try:
            db.session.remove()
        except:
            pass


def check_financial_goals() -> Dict[str, Any]:
    """
    Background job to track user financial goals against their current portfolio value.
    Sends notifications and marks goals as achieved when targets are hit.
    """
    from models import db
    
    logger.info("Running financial goals check")
    
    try:
        app = get_app()
        with app.app_context():
            from models import FinancialGoal, FinancialGoalNotification, UserPortfolio, PortfolioHolding
            from notifications import send_goal_reached_notification
            from datetime import datetime
            
            goals_achieved = 0
            
            # Fetch all active goals
            active_goals = FinancialGoal.query.filter_by(status='active').all()
            
            for goal in active_goals:
                # 1. Determine the relevant current value
                if goal.portfolio_id:
                    # Track ONLY specified portfolio
                    holdings = PortfolioHolding.query.filter_by(portfolio_id=goal.portfolio_id).all()
                else:
                    # Track WHOLE wealth (Global)
                    holdings = PortfolioHolding.query.join(UserPortfolio).filter(
                        UserPortfolio.user_id == goal.user_id
                    ).all()
                
                current_value = float(sum(h.current_value or 0 for h in holdings))
                
                # Update last checked timestamp for debugging/audit
                goal.last_checked_at = datetime.utcnow()
                
                # 2. Check if the target amount has been crossed
                if current_value >= float(goal.target_amount):
                    try:
                        # 3. Idempotency Check (Don't spam if portfolio fluctuates)
                        # Check if a notification was already sent for this specific goal
                        sent_already = FinancialGoalNotification.query.filter_by(
                            user_id=goal.user_id,
                            goal_id=goal.id
                        ).first()
                        
                        if not sent_already:
                            # Send email and push notification if requested
                            if goal.notify_on_reach:
                                send_goal_reached_notification(goal.user_id, float(goal.target_amount))
                            
                            # Mark as sent in our tracking table
                            notif = FinancialGoalNotification(
                                user_id=goal.user_id,
                                goal_id=goal.id
                            )
                            db.session.add(notif)
                            
                            # Milestone reached! 🥳
                            goal.status = 'achieved'
                            goals_achieved += 1
                            logger.info(f"Goal Reached: User {goal.user_id} hit ${goal.target_amount}")
                    except Exception as e:
                        logger.warning(f"Goal Processing Error for {goal.id}: {e}")
            
            db.session.commit()
            
            return {
                'status': 'ok', 
                'goals_achieved': goals_achieved, 
                'total_checked': len(active_goals)
            }
            
    except Exception as e:
        logger.error(f"Financial goals check failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass


def send_daily_pl_summaries() -> Dict[str, Any]:
    """
    Background job to send Daily P&L Summaries.
    Compares the most recent WealthState with the previous one to determine daily gain/loss.
    """
    from models import db
    
    logger.info("Starting Daily P&L Summary job")
    
    try:
        app = get_app()
        with app.app_context():
            from models import User, WealthState, DailySummaryNotification
            from notifications import send_daily_summary
            from services.preference_checker import should_send_notification
            from datetime import timedelta
            
            # We typically run this in the morning (e.g. 7 AM) to show yesterday's P&L
            # Or at night (e.g. 10 PM) to show 'Today's P&L'.
            # Based on cron setup, let's assume this runs AFTER the late-night snapshot.
            
            emails_sent = 0
            todays_date = datetime.utcnow().date()
            
            # 1. Get all active users
            users = User.query.filter_by(account_status='active').all()
            
            for user in users:
                try:
                    # 2. Check Preferences
                    if not should_send_notification(user.id, 'daily_summary', 'email'): 
                        # NB: 'daily_summary' isn't in pref checker yet, might fallback to 'daily_digest' or need update
                        # For now we'll assume the pref checker defaults to True or we check raw DB col if needed
                        # But let's rely on the notification handler to double check or the new col.
                        # Actually preference_checker needs update or we check manually here:
                        pass
                    
                    # Manual check of the new preference column if checker not updated
                    # (assuming user object has relationship to prefs, or we query prefs)
                    if user.notification_preferences and \
                       getattr(user.notification_preferences, 'email_portfolio_summary', True) is False:
                        continue
                    
                    # 3. Get Wealth Data
                    # Fetch latest 2 snapshots
                    snapshots = WealthState.query.filter_by(user_id=user.id)\
                        .order_by(WealthState.date.desc())\
                        .limit(2).all()
                    
                    if not snapshots:
                        continue
                        
                    latest = snapshots[0]
                    
                    # Logic: If we only have 1 snapshot, we can't show P&L (unless it's 0)
                    if len(snapshots) < 2:
                        continue
                        
                    prev = snapshots[1]
                    
                    daily_change = float(latest.total_portfolio_value or 0) - float(prev.total_portfolio_value or 0)
                    percent_change = 0
                    if float(prev.total_portfolio_value or 0) > 0:
                        percent_change = (daily_change / float(prev.total_portfolio_value)) * 100
                        
                    # 4. Idempotency Check
                    # Don't send if we already sent an email for THIS snapshot date
                    already_sent = DailySummaryNotification.query.filter_by(
                        user_id=user.id,
                        date=latest.date
                    ).first()
                    
                    if already_sent:
                        continue
                        
                    # 5. Send Notification
                    # Only send if there is significant value (user has money)
                    if float(latest.total_portfolio_value or 0) > 0:
                        send_daily_summary(
                            user_id=user.id,
                            portfolio_val=float(latest.total_portfolio_value),
                            daily_change=daily_change,
                            change_pct=percent_change
                        )
                        
                        # 6. Mark as sent
                        notif = DailySummaryNotification(
                            user_id=user.id,
                            date=latest.date
                        )
                        db.session.add(notif)
                        emails_sent += 1
                        
                except Exception as u_err:
                    logger.warning(f"Failed to process P&L summary for user {user.id}: {u_err}")
            
            db.session.commit()
            logger.info(f"Daily P&L summaries sent: {emails_sent}")
            return {'status': 'ok', 'sent': emails_sent}
            
    except Exception as e:
        logger.error(f"Daily P&L job failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass

