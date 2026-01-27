"""
News Fetch Handler
Fetches news items matching user preferences
"""
from datetime import datetime, timezone, timedelta
from models import NewsItem
import logging

logger = logging.getLogger(__name__)


def fetch_recent_news(hours_back: int = 24) -> list:
    """
    Fetch news from last N hours
    
    Args:
        hours_back: How many hours back to fetch (default: 24)
    
    Returns:
        List of NewsItem objects
    """
    try:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        news = NewsItem.query.filter(
            NewsItem.created_at >= cutoff_time,
            NewsItem.status == 'queued'  # or 'published' depending on your workflow
        ).all()
        
        logger.info(f"Fetched {len(news)} news items from last {hours_back} hours")
        return news
    
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return []


def match_news_to_user_preferences(news_item: NewsItem, user_prefs: dict) -> bool:
    """
    Check if a news item matches user's preferences
    
    Args:
        news_item: NewsItem from database
        user_prefs: Dictionary with companies, categories, news_type
    
    Returns:
        True if matches, False otherwise
    """
    try:
        companies = user_prefs.get('companies', [])
        categories = user_prefs.get('categories', [])
        news_type = user_prefs.get('news_type')
        
        # Check category match
        if categories and news_item.category not in categories:
            return False
        
        # Check company match (by symbol)
        if companies and news_item.related_symbol not in companies:
            return False
        
        # If all checks pass, it matches
        return True
    
    except Exception as e:
        logger.error(f"Error matching news: {e}")
        return False