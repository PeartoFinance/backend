"""
YFinance Rate Limiter Utility
Smart throttling and cooldown management for Yahoo Finance API calls
"""
import time
import threading
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YFinanceRateLimiter:
    """
    Smart rate limiter for Yahoo Finance requests to avoid 429 errors.
    
    Features:
    - Minimum delay between requests (prevents burst)
    - Cooldown period after 429 errors
    - Request counting per minute
    - Global lock for thread safety
    """
    _lock = threading.Lock()
    _last_request_time = datetime.min
    _request_count_window = []  # timestamps of requests in current window
    _cooldown_until = None
    _consecutive_failures = 0
    
    # Configuration
    MIN_DELAY_SECONDS = 0.3  # 300ms between requests
    MAX_REQUESTS_PER_MINUTE = 30
    COOLDOWN_DURATION_SECONDS = 60  # 1 minute cooldown
    MAX_CONSECUTIVE_FAILURES = 5  # After this, use longer cooldown
    EXTENDED_COOLDOWN_SECONDS = 300  # 5 minutes extended cooldown
    
    @classmethod
    def wait_if_needed(cls):
        """Wait if necessary before making a request. Returns True if OK to proceed."""
        with cls._lock:
            now = datetime.utcnow()
            
            # Check if in cooldown period
            if cls._cooldown_until and now < cls._cooldown_until:
                remaining = (cls._cooldown_until - now).total_seconds()
                logger.warning(f"[YFinance RateLimiter] In cooldown. {remaining:.0f}s remaining.")
                return False
            
            # Clear cooldown if expired
            if cls._cooldown_until and now >= cls._cooldown_until:
                cls._cooldown_until = None
                cls._consecutive_failures = 0
                logger.info("[YFinance RateLimiter] Cooldown expired, resuming requests")
            
            # Clean old requests from window (older than 1 minute)
            one_minute_ago = now - timedelta(minutes=1)
            cls._request_count_window = [t for t in cls._request_count_window if t > one_minute_ago]
            
            # Check request count limit
            if len(cls._request_count_window) >= cls.MAX_REQUESTS_PER_MINUTE:
                logger.warning(f"[YFinance RateLimiter] Rate limit reached ({cls.MAX_REQUESTS_PER_MINUTE}/min)")
                return False
            
            # Enforce minimum delay
            time_since_last = (now - cls._last_request_time).total_seconds()
            if time_since_last < cls.MIN_DELAY_SECONDS:
                sleep_time = cls.MIN_DELAY_SECONDS - time_since_last
                time.sleep(sleep_time)
            
            # Record this request
            cls._last_request_time = datetime.utcnow()
            cls._request_count_window.append(cls._last_request_time)
            
            return True
    
    @classmethod
    def report_success(cls):
        """Report a successful request (resets failure counter)"""
        with cls._lock:
            cls._consecutive_failures = 0
    
    @classmethod
    def report_rate_limit_error(cls):
        """Report a 429 rate limit error (triggers cooldown)"""
        with cls._lock:
            cls._consecutive_failures += 1
            
            if cls._consecutive_failures >= cls.MAX_CONSECUTIVE_FAILURES:
                cooldown = cls.EXTENDED_COOLDOWN_SECONDS
                logger.error(f"[YFinance RateLimiter] Too many failures ({cls._consecutive_failures}). Extended cooldown: {cooldown}s")
            else:
                cooldown = cls.COOLDOWN_DURATION_SECONDS
                logger.warning(f"[YFinance RateLimiter] Rate limit hit. Cooldown: {cooldown}s")
            
            cls._cooldown_until = datetime.utcnow() + timedelta(seconds=cooldown)
    
    @classmethod
    def is_in_cooldown(cls):
        """Check if currently in cooldown period"""
        with cls._lock:
            if cls._cooldown_until is None:
                return False
            return datetime.utcnow() < cls._cooldown_until
    
    @classmethod
    def get_cooldown_remaining(cls):
        """Get remaining cooldown time in seconds"""
        with cls._lock:
            if cls._cooldown_until is None:
                return 0
            remaining = (cls._cooldown_until - datetime.utcnow()).total_seconds()
            return max(0, remaining)
    
    @classmethod
    def reset(cls):
        """Reset all state (useful for testing)"""
        with cls._lock:
            cls._last_request_time = datetime.min
            cls._request_count_window = []
            cls._cooldown_until = None
            cls._consecutive_failures = 0


# Convenience function for direct usage
def check_rate_limit():
    """Check if we can make a request. Returns True if OK."""
    return YFinanceRateLimiter.wait_if_needed()


def report_yfinance_error(is_rate_limit=False):
    """Report an error from yfinance"""
    if is_rate_limit:
        YFinanceRateLimiter.report_rate_limit_error()


def report_yfinance_success():
    """Report successful yfinance call"""
    YFinanceRateLimiter.report_success()


def is_in_cooldown():
    """Check if currently in cooldown period"""
    return YFinanceRateLimiter.is_in_cooldown()
