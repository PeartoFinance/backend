"""
Jobs Package - Background Task Scheduling
Uses APScheduler for periodic market data updates and notifications
"""

from .scheduler import init_scheduler, scheduler, get_job_status
from .market_jobs import (
    update_all_stocks,
    update_all_crypto,
    update_all_indices,
    update_all_commodities,
    update_earnings_calendar,
    update_dividends,
)
from .notification_jobs import (
    check_watchlist_alerts,
    send_daily_digest,
)

__all__ = [
    'init_scheduler',
    'scheduler',
    'get_job_status',
    'update_all_stocks',
    'update_all_crypto',
    'update_all_indices',
    'update_all_commodities',
    'update_earnings_calendar',
    'update_dividends',
    'check_watchlist_alerts',
    'send_daily_digest',
]
