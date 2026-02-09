"""
News Import Jobs
Periodic jobs to fetch news from RSS feeds and external sources
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_app():
    """Get Flask app instance for use outside request context"""
    from app import app
    return app

def import_all_news() -> Dict[str, Any]:
    """
    Fetch news from all configured RSS/External sources.
    Suitable for running every 30-60 minutes via cron.
    """
    from models import db
    
    logger.info("Starting news import job")
    start_time = datetime.utcnow()
    
    try:
        from services.news_source_manager import news_source_manager
        
        app = get_app()
        with app.app_context():
            # Pull from all sources
            results = news_source_manager.pull_all_sources()
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"News import job complete: {len(results)} items fetched in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'fetched_count': len(results),
                'elapsed_seconds': elapsed,
                'message': f'Fetched {len(results)} news items'
            }
            
    except Exception as e:
        logger.error(f"News import job failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass

