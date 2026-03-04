"""
News Import Jobs
Periodic jobs to fetch news from RSS feeds and external sources
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_app():
    """Get Flask app instance for use outside request context"""
    from app import app
    return app

def import_all_news() -> Dict[str, Any]:
    """
    Fetch news from all configured RSS/External sources AND stock-specific news.
    Runs every 30 minutes via scheduler.
    """
    from models import db
    
    logger.info("Starting news import job")
    start_time = datetime.utcnow()
    rss_count = 0
    stock_news_count = 0
    
    try:
        app = get_app()
        with app.app_context():
            # 1. Pull from RSS feeds (Google News)
            try:
                from services.news_source_manager import news_source_manager
                results = news_source_manager.pull_all_sources()
                rss_count = len(results)
                logger.info(f"RSS import: {rss_count} new items")
            except Exception as e:
                logger.error(f"RSS import failed: {e}")
            
            # 2. Pull stock-specific news for listed stocks
            try:
                from models import MarketData
                from handlers.market_data.stock_handler import sync_stock_news
                
                listed_stocks = MarketData.query.filter_by(
                    is_listed=True, asset_type='stock'
                ).all()
                symbols = [s.symbol for s in listed_stocks]
                
                if symbols:
                    # Limit to 20 symbols per run to avoid API throttling
                    # Rotate through symbols each run
                    import hashlib
                    
                    # Use hour-based rotation: different subset each run
                    hour_hash = int(hashlib.md5(
                        str(datetime.utcnow().hour).encode()
                    ).hexdigest(), 16)
                    batch_size = min(20, len(symbols))
                    start_idx = hour_hash % max(1, len(symbols) - batch_size + 1)
                    batch = symbols[start_idx:start_idx + batch_size]
                    
                    logger.info(f"Stock news: fetching for {len(batch)}/{len(symbols)} symbols")
                    
                    for symbol in batch:
                        try:
                            result = sync_stock_news(symbol)
                            added = result.get('added', 0)
                            stock_news_count += added
                        except Exception as e:
                            logger.error(f"Stock news failed for {symbol}: {e}")
                        
                        # Small delay to avoid rate limiting
                        time.sleep(0.5)
                    
                    logger.info(f"Stock news import: {stock_news_count} new items")
            except Exception as e:
                logger.error(f"Stock news import failed: {e}")
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            total = rss_count + stock_news_count
            logger.info(f"News import complete: {total} items ({rss_count} RSS + {stock_news_count} stock) in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'rss_count': rss_count,
                'stock_news_count': stock_news_count,
                'total_count': total,
                'elapsed_seconds': elapsed,
                'message': f'Fetched {total} news items'
            }
            
    except Exception as e:
        logger.error(f"News import job failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass


def cleanup_old_articles() -> Dict[str, Any]:
    """
    Delete news articles older than 20 days.
    Runs daily at 2 AM UTC via scheduler.
    """
    from models import db
    from models.article import NewsItem

    logger.info("Starting old articles cleanup job")
    start_time = datetime.utcnow()
    deleted_count = 0

    try:
        app = get_app()
        with app.app_context():
            cutoff = datetime.utcnow() - timedelta(days=20)
            deleted_count = NewsItem.query.filter(
                NewsItem.created_at < cutoff
            ).delete(synchronize_session=False)
            db.session.commit()
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Cleanup complete: {deleted_count} articles deleted (older than {cutoff.date()}) in {elapsed:.1f}s")
            return {
                'status': 'ok',
                'deleted_count': deleted_count,
                'cutoff_date': cutoff.isoformat(),
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Article cleanup job failed: {e}")
        return {'status': 'error', 'error': str(e)}
    finally:
        try:
            db.session.remove()
        except:
            pass
