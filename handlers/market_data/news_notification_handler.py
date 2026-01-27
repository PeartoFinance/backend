"""
News Notification Job
Main cron job logic: fetch news → match preferences → send notifications
"""
from datetime import datetime, timezone
from models import User, NewsPreference, NewsNotification, NewsItem, UserNotificationPref
from models.base import db
from .news_fetch_handler import fetch_recent_news, match_news_to_user_preferences
from notifications.push_service import send_push_notification
from handlers.email_service import send_email
import logging
import os

logger = logging.getLogger(__name__)

# Get app URL from environment, default to placeholder
APP_URL = os.getenv('APP_URL', 'https://pearto.com')


def process_news_notifications() -> dict:
    """
    Main cron job function
    1. Fetch recent news
    2. For each user with preferences
    3. Match news to preferences
    4. Skip if already sent
    5. Send notifications (log + email + push)
    6. Record in news_notifications table
    
    Returns:
        Result dictionary with counts
    """
    
    result = {
        'success': True,
        'total_news': 0,
        'users_processed': 0,
        'notifications_sent': 0,
        'duplicates_skipped': 0,
        'errors': 0
    }
    
    try:
        # Step 1: Fetch recent news (last 24 hours)
        recent_news = fetch_recent_news(hours_back=24)
        result['total_news'] = len(recent_news)
        
        if not recent_news:
            logger.info("No recent news found")
            return result
        
        # Step 2: Get all users with news preferences
        users_with_prefs = NewsPreference.query.all()
        result['users_processed'] = len(users_with_prefs)
        
        logger.info(f"Processing news for {len(users_with_prefs)} users")
        
        # Step 3: For each user
        for user_pref in users_with_prefs:
            user_id = user_pref.user_id
            
            try:
                # Get user object
                user = User.query.get(user_id)
                if not user:
                    logger.warning(f"User {user_id} not found")
                    continue
                
                # Get user's notification preferences
                notif_prefs = UserNotificationPref.query.filter_by(user_id=user_id).first()
                
                # Check if user wants news notifications
                if notif_prefs and not notif_prefs.email_news and not notif_prefs.push_news:
                    logger.debug(f"User {user_id} has notifications disabled")
                    continue
                
                # Step 4: Match news to this user's preferences
                for news_item in recent_news:
                    
                    # Check if news matches preferences
                    if not match_news_to_user_preferences(news_item, {
                        'companies': user_pref.companies,
                        'categories': user_pref.categories,
                        'news_type': user_pref.news_type
                    }):
                        continue
                    
                    # Step 5: Check if already sent
                    already_sent = NewsNotification.query.filter_by(
                        user_id=user_id,
                        news_id=news_item.id
                    ).first()
                    
                    if already_sent:
                        result['duplicates_skipped'] += 1
                        logger.debug(f"News {news_item.id} already sent to user {user_id}")
                        continue
                    
                    # Step 6: Send notifications
                    try:
                        send_user_notification(user, news_item, notif_prefs)
                        result['notifications_sent'] += 1
                        
                        # Record in database (prevents duplicates)
                        notification_record = NewsNotification(
                            user_id=user_id,
                            news_id=news_item.id,
                            sent_at=datetime.now(timezone.utc)
                        )
                        db.session.add(notification_record)
                        
                    except Exception as e:
                        result['errors'] += 1
                        logger.error(f"Error sending notification to user {user_id}: {e}")
                
            except Exception as e:
                result['errors'] += 1
                logger.error(f"Error processing user {user_id}: {e}")
        
        # Commit all notification records
        db.session.commit()
        
        logger.info(f"News notification job completed: {result}")
        
    except Exception as e:
        result['success'] = False
        result['errors'] += 1
        logger.error(f"Critical error in news notification job: {e}")
        db.session.rollback()
    
    return result


def send_user_notification(user: 'User', news_item: NewsItem, notif_prefs: 'UserNotificationPref') -> None:
    """
    Send notification to user via all channels
    Tries both email and push - if one fails, other still might work
    
    Args:
        user: User object
        news_item: NewsItem object
        notif_prefs: UserNotificationPref object
    """
    
    title = f"News: {news_item.title[:60]}"
    message = news_item.summary or news_item.title
    news_url = f"{APP_URL}/news/{news_item.slug}" if news_item.slug else news_item.canonical_url
    
    # Step 1: Log the notification (always)
    logger.info(f"Sending news notification - User: {user.id}, News: {news_item.id}, Title: {news_item.title[:50]}")
    
    # Step 2: Try email
    email_sent = False
    if notif_prefs and notif_prefs.email_news:
        try:
            send_email(
                to=user.email,
                template='news_notification',
                subject=title,
                variables={
                    'user_name': user.name,
                    'news_title': news_item.title,
                    'news_summary': message,
                    'news_url': news_url,
                    'news_image': news_item.image or '/placeholder.svg',
                    'news_source': news_item.source or 'Pearto'
                }
            )
            email_sent = True
            logger.debug(f"Email sent to user {user.id}")
        except Exception as e:
            logger.warning(f"Failed to send email to user {user.id}: {e}")
    
    # Step 3: Try push notification
    push_sent = False
    if notif_prefs and notif_prefs.push_news:
        try:
            push_result = send_push_notification(
                user_id=user.id,
                title=title,
                message=message,
                url=news_url,
                data={'news_id': news_item.id, 'news_url': news_url}
            )
            if push_result.get('status') != 'error':
                push_sent = True
                logger.debug(f"Push notification sent to user {user.id}")
        except Exception as e:
            logger.warning(f"Failed to send push to user {user.id}: {e}")
    
    # Log result
    if email_sent or push_sent:
        logger.info(f"Notification delivered to user {user.id} (email: {email_sent}, push: {push_sent})")
    else:
        logger.warning(f"Could not deliver notification to user {user.id}")