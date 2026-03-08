"""
Background Job Scheduler
Uses APScheduler for periodic background tasks.
Supports standard parallel execution or sequential database-backed execution.
"""
import os
import logging
import json
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from flask import current_app

from services.settings_service import get_setting_secure

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None
_app = None

def get_job_config():
    """Get job configuration dynamically"""
    return {
        'stocks_interval_minutes': int(get_setting_secure('JOB_STOCKS_INTERVAL', 15)),
        'crypto_interval_minutes': int(get_setting_secure('JOB_CRYPTO_INTERVAL', 5)),
        'indices_interval_minutes': int(get_setting_secure('JOB_INDICES_INTERVAL', 5)),
        'commodities_interval_minutes': int(get_setting_secure('JOB_COMMODITIES_INTERVAL', 15)),
        'watchlist_interval_seconds': int(get_setting_secure('JOB_WATCHLIST_INTERVAL', 60)),
        'calendar_hour': int(get_setting_secure('JOB_CALENDAR_HOUR', 6)),  # 6 AM
    }

def get_cron_mode():
    """Get cron mode dynamically"""
    return get_setting_secure('CRON_MODE', 'parallel').lower()


def init_scheduler(app=None):
    """
    Initialize the APScheduler with Flask app context.
    Call this after Flask app is created.
    """
    global scheduler, _app
    
    if scheduler is not None:
        logger.warning("Scheduler already initialized")
        return scheduler
        
    if app:
        _app = app
    
    jobstores = {
        'default': MemoryJobStore()
    }
    
    # In shared hosting, we must keep threads Very Low to avoid 'fork() failed'
    # 5 threads is usually the safe limit for background workers
    pool_size = 5 
    
    # Optimized for production: 20 threads was causing "fork() failed" on many hosting environments.
    # Reducing to 5 ensures the server has enough resources for real users.
    executors = {
        'default': ThreadPoolExecutor(5),
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
    
    # Register queue processor if in sequential mode
    cron_mode = get_cron_mode()
    if cron_mode == 'sequential':
        _register_queue_processor(app)
        logger.info("Scheduler initialized in SEQUENTIAL mode (database queue)")
    else:
        logger.info("Scheduler initialized in PARALLEL mode (standard)")
    
    # Start scheduler
    scheduler.start()
    
    return scheduler


def queue_job(func, job_name, *args, **kwargs):
    """
    Wrapper to either run job immediately or queue it based on CRON_MODE.
    Usage: scheduler.add_job(lambda: queue_job(actual_func, 'job_name'), ...)
    """
    if get_cron_mode() == 'sequential':
        # Define inner logic to run within context
        def _enqueue():
            try:
                from models.cron_job import CronJob, JobStatus
                from models.base import db
                
                # Check if job is already pending to avoid duplicates
                existing = CronJob.query.filter_by(
                    job_name=job_name, 
                    status=JobStatus.PENDING
                ).first()
                
                if existing:
                    logger.info(f"Job {job_name} already pending, skipping enqueue")
                    return
                    
                job = CronJob(
                    job_name=job_name,
                    params=json.dumps({'args': args, 'kwargs': kwargs}) if args or kwargs else None,
                    status=JobStatus.PENDING
                )
                db.session.add(job)
                db.session.commit()
                logger.info(f"Enqueued job: {job_name}")
                db.session.remove()
                
            except Exception as e:
                logger.error(f"Failed to enqueue job {job_name}: {e}")
        
        # Check for application context
        try:
            # If we are in a request or app context, this works
            if current_app:
                _enqueue()
        except RuntimeError:
            # No application context (background thread), use stored app
            if _app:
                with _app.app_context():
                    _enqueue()
            else:
                logger.error("Cannot enqueue job: No application context available and _app not set")

    else:
        # Run immediately (standard behavior)
        logger.info(f"Running job immediately: {job_name}")
        func(*args, **kwargs)


def _register_queue_processor(app):
    """Register the job that processes the queue sequentially"""
    scheduler.add_job(
        lambda: process_job_queue(app),
        'interval',
        seconds=30,  # Check queue every 30 seconds
        id='process_job_queue',
        name='Process Job Queue',
        replace_existing=True
    )


def process_job_queue(app):
    """
    Worker function to process pending jobs one by one.
    This runs in its own thread/process but executes jobs sequentially.
    """
    with app.app_context():
        from models.cron_job import CronJob, JobStatus
        from models.base import db
        
        # Get pending jobs ordered by creation time
        # processing one at a time to ensure sequential execution
        # We fetch one, execute, then fetch next to handle long-running jobs correctly
        # But since valid execution context is needed, we do a loop here
        
        # Limit to processing for a max duration to avoid holding the thread too long
        # or just process one batch. 
        # Let's process until queue is empty or hitting a limit
        
        processed_count = 0
        max_jobs_per_run = 5 
        
        while processed_count < max_jobs_per_run:
            try:
                # Lock the next job
                job = CronJob.query.filter_by(status=JobStatus.PENDING)\
                    .order_by(CronJob.created_at.asc())\
                    .with_for_update()\
                    .first()
                
                if not job:
                    break
                    
                # Mark as processing
                job.status = JobStatus.PROCESSING
                job.started_at = datetime.utcnow()
                db.session.commit()
                
                logger.info(f"Processing queued job: {job.job_name} (ID: {job.id})")
                
                # Execute the job
                try:
                     _execute_job_by_name(job.job_name, job.params)
                     job.status = JobStatus.COMPLETED
                     job.result = "Success"
                except Exception as e:
                    logger.error(f"Job {job.job_name} failed: {e}")
                    job.status = JobStatus.FAILED
                    job.error = str(e)
                
                job.completed_at = datetime.utcnow()
                db.session.commit()
                processed_count += 1
                
                # IMPORTANT: Release the connection back to the pool after each heavy job
                # This prevents "Connection Camping" during background processing
                db.session.remove()
                
            except Exception as e:
                logger.error(f"Error in queue processor: {e}")
                db.session.rollback()
                time.sleep(1) # Backoff
                break


def _execute_job_by_name(job_name, params_json):
    """Resolves job string name to function and calls it"""
    # Import all job modules
    # Import all job modules
    from .market_jobs import (
        update_all_stocks, update_all_crypto, update_all_indices,
        update_all_commodities, update_earnings_calendar, update_dividends,
        update_business_profiles, update_financials, update_all_forex,
        update_all_forecasts, update_ytd_returns
    )
    from .notification_jobs import (
        check_watchlist_alerts, send_daily_digest, check_earnings_alerts,
        send_daily_pl_summaries, check_financial_goals, process_news_notifications,
        check_trial_expirations
    )
    from .system_jobs import snapshot_user_wealth, cleanup_deleted_accounts
    from .news_jobs import import_all_news, cleanup_old_articles
    from handlers.market_data.forecast_handler import sync_forecast_data
    from services.sports_import_service import SportsImportService
    
    # Map names to functions
    # Using a mapping ensures safe execution of only allowed functions
    job_map = {
        'update_all_stocks': update_all_stocks,
        'update_all_crypto': update_all_crypto,
        'update_all_indices': update_all_indices,
        'update_all_commodities': update_all_commodities,
        'update_earnings_calendar': update_earnings_calendar,
        'update_dividends': update_dividends,
        'update_business_profiles': update_business_profiles,
        'update_financials': update_financials,
        'update_all_forex': update_all_forex,
        'update_all_forecasts': update_all_forecasts,
        'update_ytd_returns': update_ytd_returns,
        
        'check_watchlist_alerts': check_watchlist_alerts,
        'send_daily_digest': send_daily_digest,
        'check_earnings_alerts': check_earnings_alerts,
        'send_daily_pl_summaries': send_daily_pl_summaries,
        'check_financial_goals': check_financial_goals,
        'process_news_notifications': process_news_notifications,
        'check_trial_expirations': check_trial_expirations,
        
        'snapshot_user_wealth': snapshot_user_wealth,
        'cleanup_deleted_accounts': cleanup_deleted_accounts,
        'import_all_news': import_all_news,
        'cleanup_old_articles': cleanup_old_articles,
        'sync_forecast_data': sync_forecast_data,
        
        # Sports Jobs (Added for sequential processing)
        'sports_import': SportsImportService.import_events,
        'sports_live_refresh': SportsImportService.refresh_live_events
    }
    
    func = job_map.get(job_name)
    if not func:
        raise ValueError(f"Unknown job function: {job_name}")
        
    args = []
    kwargs = {}
    if params_json:
        params = json.loads(params_json)
        args = params.get('args', [])
        kwargs = params.get('kwargs', {})
        
    func(*args, **kwargs)


def _register_market_jobs():
    """Register all market data update jobs"""
    # We use lambda to defer execution to queue_job wrapper
    
    from .market_jobs import (
        update_all_stocks, update_all_crypto, update_all_indices,
        update_all_commodities, update_earnings_calendar, update_dividends,
        update_business_profiles, update_ytd_returns, update_all_forecasts
    )
    
    # Calculate a small delay (2 mins) to allow server to settle after push/restart
    # This prevents immediate heavy API calls to Yahoo right after boot
    start_date = datetime.utcnow() + timedelta(minutes=2)
    
    # YTD Returns update (Daily at 1 AM)
    scheduler.add_job(
        lambda: queue_job(update_ytd_returns, 'update_ytd_returns'),
        'cron',
        hour=1,
        id='update_ytd',
        name='Update YTD Returns',
        replace_existing=True
    )
    
    # Stock updates
    job_config = get_job_config()
    scheduler.add_job(
        lambda: queue_job(update_all_stocks, 'update_all_stocks'),
        'interval',
        minutes=job_config['stocks_interval_minutes'],
        start_date=start_date,
        id='update_stocks',
        name='Update Stock Prices',
        replace_existing=True
    )
    
    # Crypto updates
    scheduler.add_job(
        lambda: queue_job(update_all_crypto, 'update_all_crypto'),
        'interval',
        minutes=job_config['crypto_interval_minutes'],
        start_date=start_date,
        id='update_crypto',
        name='Update Crypto Prices',
        replace_existing=True
    )
    
    # Index updates
    scheduler.add_job(
        lambda: queue_job(update_all_indices, 'update_all_indices'),
        'interval',
        minutes=job_config['indices_interval_minutes'],
        start_date=start_date,
        id='update_indices',
        name='Update Market Indices',
        replace_existing=True
    )
    
    # Commodity updates
    scheduler.add_job(
        lambda: queue_job(update_all_commodities, 'update_all_commodities'),
        'interval',
        minutes=job_config['commodities_interval_minutes'],
        start_date=start_date,
        id='update_commodities',
        name='Update Commodities',
        replace_existing=True
    )
    
    # Earnings calendar
    scheduler.add_job(
        lambda: queue_job(update_earnings_calendar, 'update_earnings_calendar'),
        'cron',
        hour=job_config['calendar_hour'],
        id='update_earnings',
        name='Update Earnings Calendar',
        replace_existing=True
    )
    
    # Dividends
    scheduler.add_job(
        lambda: queue_job(update_dividends, 'update_dividends'),
        'cron',
        hour=job_config['calendar_hour'],
        minute=30,
        id='update_dividends',
        name='Update Dividends',
        replace_existing=True
    )
    
    # Business Profiles
    scheduler.add_job(
        lambda: queue_job(update_business_profiles, 'update_business_profiles'),
        'cron',
        day_of_week='sun',
        hour=2,
        id='update_business_profiles',
        name='Sync Business Profiles',
        replace_existing=True
    )
    
    # Forecasts (daily at 3 AM)
    scheduler.add_job(
        lambda: queue_job(update_all_forecasts, 'update_all_forecasts'),
        'cron',
        hour=3,
        id='update_forecasts',
        name='Update Analyst Forecasts',
        replace_existing=True
    )
    
    logger.info("Market jobs registered")


def _register_notification_jobs():
    """Register notification and alert jobs"""
    from .notification_jobs import (
        check_watchlist_alerts, send_daily_digest, check_earnings_alerts,
        send_daily_pl_summaries, process_news_notifications, check_trial_expirations
    )
    from .news_jobs import import_all_news, cleanup_old_articles
    
    start_date = datetime.utcnow() + timedelta(minutes=2)
    
    # Watchlist price alerts
    job_config = get_job_config()
    scheduler.add_job(
        lambda: queue_job(check_watchlist_alerts, 'check_watchlist_alerts'),
        'interval',
        seconds=job_config['watchlist_interval_seconds'],
        start_date=start_date,
        id='check_watchlist',
        name='Check Watchlist Alerts',
        replace_existing=True
    )

    # Earnings alerts
    scheduler.add_job(
        lambda: queue_job(check_earnings_alerts, 'check_earnings_alerts'),
        'cron',
        hour=7,
        id='earnings_alerts',
        name='Check Earnings Alerts',
        replace_existing=True
    )
    
    # Daily digest
    scheduler.add_job(
        lambda: queue_job(send_daily_digest, 'send_daily_digest'),
        'cron',
        hour=9,
        id='daily_digest',
        name='Send Daily Digest',
        replace_existing=True
    )
    
    # Daily P&L Summary
    scheduler.add_job(
        lambda: queue_job(send_daily_pl_summaries, 'send_daily_pl_summaries'),
        'cron',
        hour=8,
        id='daily_pl_summary',
        name='Send Daily P&L Summary',
        replace_existing=True
    )

    # Trial Expiration Reminders (Daily at 10 AM)
    scheduler.add_job(
        lambda: queue_job(check_trial_expirations, 'check_trial_expirations'),
        'cron',
        hour=10,
        id='trial_reminders',
        name='Trial Expiration Reminders',
        replace_existing=True
    )
    
    logger.info("Notification jobs registered")
    
    # System maintenance jobs
    from .system_jobs import snapshot_user_wealth
    
    # Wealth snapshot
    scheduler.add_job(
        lambda: queue_job(snapshot_user_wealth, 'snapshot_user_wealth'),
        'cron',
        hour=23,
        minute=59,
        id='wealth_snapshot',
        name='Daily Wealth Snapshot',
        replace_existing=True
    )
    
    # News import
    scheduler.add_job(
        lambda: queue_job(import_all_news, 'import_all_news'),
        'interval',
        minutes=30,
        start_date=start_date,
        id='import_news',
        name='Import News',
        replace_existing=True
    )
    
    # News notifications
    scheduler.add_job(
        lambda: queue_job(process_news_notifications, 'process_news_notifications'),
        'interval',
        minutes=60,
        id='news_notifications',
        name='News Notifications',
        replace_existing=True
    )

    # Old article cleanup (daily at 2 AM UTC)
    scheduler.add_job(
        lambda: queue_job(cleanup_old_articles, 'cleanup_old_articles'),
        'cron',
        hour=2,
        minute=0,
        id='cleanup_old_articles',
        name='Clean Up Old Articles',
        replace_existing=True
    )

    logger.info("System jobs registered")


def get_job_status():
    """Get status of all scheduled jobs"""
    if scheduler is None:
        return {'status': 'not_initialized', 'jobs': []}
    
    jobs = []
    # Regular scheduled jobs
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
            'trigger': str(job.trigger),
            'pending': job.pending,
        })
    
    # If in sequential mode, also fetch pending queue stats
    queue_stats = {}
    cron_mode = get_cron_mode()
    if cron_mode == 'sequential':
        try:
            from models.cron_job import CronJob, JobStatus
            pending_count = CronJob.query.filter_by(status=JobStatus.PENDING).count()
            processing_count = CronJob.query.filter_by(status=JobStatus.PROCESSING).count()
            failed_count = CronJob.query.filter_by(status=JobStatus.FAILED).count()
            
            queue_stats = {
                'pending_jobs': pending_count,
                'processing_jobs': processing_count,
                'failed_jobs_total': failed_count
            }
        except:
            pass
    
    return {
        'status': 'running' if scheduler.running else 'stopped',
        'mode': get_cron_mode(),
        'jobs': jobs,
        'queue_stats': queue_stats,
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
    """Manually trigger a job to run (or enqueue) immediately"""
    if scheduler:
        job = scheduler.get_job(job_id)
        if job:
            # We EXECUTE the function directly here
            # because the function itself (as registered) 
            # already contains the queue_job wrapper logic if applicable
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
