"""
System Maintenance Jobs
PeartoFinance Backend

This file contains background tasks for system maintenance, such as
cleaning up old data and optimizing the database.
"""

import logging
from datetime import datetime, timedelta, timezone
from models import (
    db, User, UserPortfolio, PortfolioHolding, PortfolioTransaction,
    Watchlist, WatchlistItem, UserWatchlist, UserAlert, 
    UserNotificationPref, UserDashboardConfig, UserDevice,
    UserActivity, UserDocument, UserSession, PasswordResetToken,
    LoginEvent, AdminUser, WealthState
)

logger = logging.getLogger(__name__)

def snapshot_user_wealth():
    """
    Daily snapshot of user wealth (portfolio value + cash).
    Used for net worth history charts.
    """
    try:
        from app import app
        with app.app_context():
            # 1. Get all active users
            users = User.query.filter_by(account_status='active').all()
            today = datetime.now(timezone.utc).date()
            
            snapshots_created = 0
            
            for user in users:
                # 2. Calculate total portfolio value for this user
                # Sum of all holdings across all portfolios
                holdings = PortfolioHolding.query.join(UserPortfolio).filter(
                    UserPortfolio.user_id == user.id
                ).all()
                
                total_portfolio_value = sum(float(h.current_value or 0) for h in holdings)
                
                # 3. Check if snapshot for today already exists (to avoid duplicates)
                existing = WealthState.query.filter_by(
                    user_id=user.id,
                    date=today
                ).first()
                
                if existing:
                    # Update existing snapshot
                    existing.total_portfolio_value = total_portfolio_value
                    # Calculate daily change if previous day exists
                    yesterday = today - timedelta(days=1)
                    prev = WealthState.query.filter_by(user_id=user.id, date=yesterday).first()
                    if prev:
                        existing.daily_change = total_portfolio_value - float(prev.total_portfolio_value or 0)
                else:
                    # Create new snapshot
                    daily_change = 0
                    yesterday = today - timedelta(days=1)
                    prev = WealthState.query.filter_by(user_id=user.id, date=yesterday).first()
                    if prev:
                        daily_change = total_portfolio_value - float(prev.total_portfolio_value or 0)
                        
                    snapshot = WealthState(
                        user_id=user.id,
                        date=today,
                        total_portfolio_value=total_portfolio_value,
                        total_cash=0, # Placeholder for future cash tracking
                        total_investments=total_portfolio_value,
                        daily_change=daily_change
                    )
                    db.session.add(snapshot)
                
                snapshots_created += 1
                
            db.session.commit()
            logger.info(f"Wealth snapshot complete: {snapshots_created} users processed.")
            return {'status': 'ok', 'processed': snapshots_created}
            
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during wealth snapshot: {str(e)}")
        return {'status': 'error', 'error': str(e)}


def cleanup_deleted_accounts():
    """
    Permanently deletes accounts that have been marked as 'deleted' 
    for more than 30 days. This is a 'Hard Delete' to save space
    and comply with privacy regulations.
    """
    try:
        # 1. Find users marked as 'deleted' more than 30 days ago
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=30)
        users_to_delete = User.query.filter(
            User.account_status == 'deleted',
            User.deactivated_at <= cutoff_date
        ).all()

        if not users_to_delete:
            logger.info("No old deleted accounts to clean up.")
            return

        logger.info(f"Found {len(users_to_delete)} accounts to permanently delete.")

        for user in users_to_delete:
            user_id = user.id
            logger.info(f"Hard deleting user ID: {user_id} ({user.email})")

            # 2. Delete Portfolio Data
            portfolios = UserPortfolio.query.filter_by(user_id=user_id).all()
            for p in portfolios:
                PortfolioTransaction.query.filter_by(portfolio_id=p.id).delete()
                PortfolioHolding.query.filter_by(portfolio_id=p.id).delete()
                db.session.delete(p)

            # 3. Delete Watchlist Data
            watchlists = Watchlist.query.filter_by(user_id=user_id).all()
            for w in watchlists:
                WatchlistItem.query.filter_by(watchlist_id=w.id).delete()
                db.session.delete(w)
            
            UserWatchlist.query.filter_by(user_id=user_id).delete()

            # 4. Delete Other User-Related Data
            UserAlert.query.filter_by(user_id=user_id).delete()
            UserNotificationPref.query.filter_by(user_id=user_id).delete()
            UserDashboardConfig.query.filter_by(user_id=user_id).delete()
            UserDevice.query.filter_by(user_id=user_id).delete()
            UserActivity.query.filter_by(user_id=user_id).delete()
            UserDocument.query.filter_by(user_id=user_id).delete()
            UserSession.query.filter_by(user_id=user_id).delete()
            PasswordResetToken.query.filter_by(user_id=user_id).delete()
            LoginEvent.query.filter_by(user_id=user_id).delete()
            AdminUser.query.filter_by(user_id=user_id).delete()

            # 5. Finally, delete the User record
            db.session.delete(user)

        # Commit all deletions
        db.session.commit()
        logger.info(f"Successfully cleaned up {len(users_to_delete)} accounts.")

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error during deleted accounts cleanup: {str(e)}")
