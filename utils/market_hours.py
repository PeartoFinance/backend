"""
Market Hours Utility
Check if major markets are currently open to avoid stale cron updates.
"""
from datetime import datetime
import pytz
import logging

logger = logging.getLogger(__name__)

# Fallback trading schedule when MarketHours table is empty or unavailable.
# Uses US market (NYSE) as the default reference.
_FALLBACK_SCHEDULE = {
    'timezone': 'America/New_York',
    'open_time': '09:30',
    'close_time': '16:00',
    'trading_days': ['MON', 'TUE', 'WED', 'THU', 'FRI'],
}

_DAY_MAP = {0: 'MON', 1: 'TUE', 2: 'WED', 3: 'THU', 4: 'FRI', 5: 'SAT', 6: 'SUN'}


def is_any_major_market_open() -> bool:
    """
    Returns True if at least one active exchange in MarketHours is currently
    within its trading window.  Falls back to the US (NYSE) schedule when the
    database table is empty or inaccessible.
    """
    try:
        from models.settings import MarketHours
        exchanges = MarketHours.query.filter_by(is_active=True).all()

        if not exchanges:
            # No rows in the table – use fallback
            return _is_open_for_schedule(_FALLBACK_SCHEDULE)

        for ex in exchanges:
            schedule = {
                'timezone': ex.timezone,
                'open_time': ex.open_time,
                'close_time': ex.close_time,
                'trading_days': ex.trading_days.split(',') if ex.trading_days else _FALLBACK_SCHEDULE['trading_days'],
            }
            if _is_open_for_schedule(schedule):
                return True
        return False

    except Exception as e:
        logger.warning(f"[market_hours] Could not query MarketHours table ({e}), using fallback")
        return _is_open_for_schedule(_FALLBACK_SCHEDULE)


def is_us_market_open() -> bool:
    """Quick check: is the US stock market (NYSE) currently open?"""
    try:
        from models.settings import MarketHours
        nyse = MarketHours.query.filter_by(exchange_code='NYSE', is_active=True).first()
        if nyse:
            schedule = {
                'timezone': nyse.timezone,
                'open_time': nyse.open_time,
                'close_time': nyse.close_time,
                'trading_days': nyse.trading_days.split(',') if nyse.trading_days else _FALLBACK_SCHEDULE['trading_days'],
            }
            return _is_open_for_schedule(schedule)
    except Exception:
        pass
    return _is_open_for_schedule(_FALLBACK_SCHEDULE)


def get_market_status_summary() -> dict:
    """
    Returns a compact summary suitable for including in API responses.
    {
        "anyMarketOpen": bool,
        "usMarketOpen": bool,
        "label": "Markets Open" | "Markets Closed"
    }
    """
    any_open = is_any_major_market_open()
    us_open = is_us_market_open()
    return {
        'anyMarketOpen': any_open,
        'usMarketOpen': us_open,
        'label': 'Markets Open' if any_open else 'Markets Closed',
    }


# ── internal helper ──────────────────────────────────────────────

def _is_open_for_schedule(schedule: dict) -> bool:
    """Check if the current moment falls within the given trading window."""
    try:
        tz = pytz.timezone(schedule['timezone'])
        now = datetime.now(tz)
        today = _DAY_MAP[now.weekday()]

        if today not in schedule['trading_days']:
            return False

        open_h, open_m = (int(x) for x in schedule['open_time'].split(':'))
        close_h, close_m = (int(x) for x in schedule['close_time'].split(':'))

        open_dt = now.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
        close_dt = now.replace(hour=close_h, minute=close_m, second=0, microsecond=0)

        return open_dt <= now <= close_dt
    except Exception as e:
        logger.warning(f"[market_hours] schedule check error: {e}")
        return False
