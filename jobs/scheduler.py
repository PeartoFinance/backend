"""
Background Job Scheduler
Uses APScheduler for periodic background tasks
"""
import os
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None

# Job configuration from environment
JOB_CONFIG = {
    'stocks_interval_minutes': int(os.getenv('JOB_STOCKS_INTERVAL', 15)),
    'crypto_interval_minutes': int(os.getenv('JOB_CRYPTO_INTERVAL', 5)),
    'indices_interval_minutes': int(os.getenv('JOB_INDICES_INTERVAL', 5)),
    'commodities_interval_minutes': int(os.getenv('JOB_COMMODITIES_INTERVAL', 15)),
    'watchlist_interval_seconds': int(os.getenv('JOB_WATCHLIST_INTERVAL', 60)),
    'calendar_hour': int(os.getenv('JOB_CALENDAR_HOUR', 6)),  # 6 AM
}


def init_scheduler(app=None):
    """
    Initialize the APScheduler with Flask app context.
    Call this after Flask app is created.
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
    
    jobstores = {
        'default': MemoryJobStore()
    }
    
    executors = {
        'default': ThreadPoolExecutor(10),
    }
    
    job_defaults = {
        'coalesce': True,  # Combine missed jobs into one
        'max_instances': 1,  # Only one instance of each job at a time
        'misfire_grace_time': 60,  # Allow 60s delay
    }
    
    scheduler = BackgroundScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone='UTC'
    )
    
    # Register jobs
    _register_market_jobs()
    _register_notification_jobs()
    
    # Start scheduler
    scheduler.start()
    logger.info("Background scheduler started")
    
    return scheduler


def _register_market_jobs():
    """Register all market data update jobs"""
    from .market_jobs import (
        update_all_stocks,
        update_all_crypto,
        update_all_indices,
        update_all_commodities,
        update_earnings_calendar,
        update_dividends,
        update_business_profiles,
    )
    
    # Stock updates - every 15 min (configurable)
    scheduler.add_job(
        update_all_stocks,
        'interval',
        minutes=JOB_CONFIG['stocks_interval_minutes'],
        id='update_stocks',
        name='Update Stock Prices',
        replace_existing=True
    )
    
    # Crypto updates - every 5 min (24/7)
    scheduler.add_job(
        update_all_crypto,
        'interval',
        minutes=JOB_CONFIG['crypto_interval_minutes'],
        id='update_crypto',
        name='Update Crypto Prices',
        replace_existing=True
    )
    
    # Index updates - every 5 min
    scheduler.add_job(
        update_all_indices,
        'interval',
        minutes=JOB_CONFIG['indices_interval_minutes'],
        id='update_indices',
        name='Update Market Indices',
        replace_existing=True
    )
    
    # Commodity updates - every 15 min
    scheduler.add_job(
        update_all_commodities,
        'interval',
        minutes=JOB_CONFIG['commodities_interval_minutes'],
        id='update_commodities',
        name='Update Commodities',
        replace_existing=True
    )
    
    # Earnings calendar - daily at 6 AM UTC
    scheduler.add_job(
        update_earnings_calendar,
        'cron',
        hour=JOB_CONFIG['calendar_hour'],
        id='update_earnings',
        name='Update Earnings Calendar',
        replace_existing=True
    )
    
    # Dividends - daily at 6 AM UTC
    scheduler.add_job(
        update_dividends,
        'cron',
        hour=JOB_CONFIG['calendar_hour'],
        minute=30,
        id='update_dividends',
        name='Update Dividends',
        replace_existing=True
    )
    
    # Business Profiles (Financials + Forecasts) - weekly on Sunday at 2 AM UTC
    scheduler.add_job(
        update_business_profiles,
        'cron',
        day_of_week='sun',
        hour=2,
        id='update_business_profiles',
        name='Sync Business Profiles (Financials/Forecasts)',
        replace_existing=True
    )
    
    logger.info("Market jobs registered")


def _register_notification_jobs():
    """Register notification and alert jobs"""
    from .notification_jobs import (
        check_watchlist_alerts,
        send_daily_digest,
    )
    
    # Watchlist price alerts - every 60 seconds
    scheduler.add_job(
        check_watchlist_alerts,
        'interval',
        seconds=JOB_CONFIG['watchlist_interval_seconds'],
        id='check_watchlist',
        name='Check Watchlist Alerts',
        replace_existing=True
    )
    
    # Daily digest - 9 AM UTC
    scheduler.add_job(
        send_daily_digest,
        'cron',
        hour=9,
        id='daily_digest',
        name='Send Daily Digest',
        replace_existing=True
    )
    
    logger.info("Notification jobs registered")



def get_job_status():
    """Get status of all scheduled jobs"""
    if scheduler is None:
        return {'status': 'not_initialized', 'jobs': []}
    
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger),
            'pending': job.pending,
        })
    
    return {
        'status': 'running' if scheduler.running else 'stopped',
        'jobs': jobs,
        'timestamp': datetime.utcnow().isoformat()
    }


def pause_job(job_id: str):
    """Pause a specific job"""
    if scheduler:
        scheduler.pause_job(job_id)
        return True
    return False


def resume_job(job_id: str):
    """Resume a paused job"""
    if scheduler:
        scheduler.resume_job(job_id)
        return True
    return False


def run_job_now(job_id: str):
    """Manually trigger a job to run immediately"""
    if scheduler:
        job = scheduler.get_job(job_id)
        if job:
            job.func()
            return True
    return False


def shutdown_scheduler():
    """Gracefully shutdown the scheduler"""
    global scheduler
    if scheduler:
        scheduler.shutdown(wait=False)
        scheduler = None
        logger.info("Scheduler shutdown complete")
