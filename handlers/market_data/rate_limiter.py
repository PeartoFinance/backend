"""
YFinance Rate Limiter Utility
Smart throttling and cooldown management for Yahoo Finance API calls.

Uses DUAL BUCKETS to prevent background cron jobs from blocking live user requests:
  - 'live'       → shorter cooldowns, used by API route handlers (default)
  - 'background' → longer cooldowns, used by cron/market_jobs only
"""
import time
import threading
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class YFinanceRateLimiter:
    """
    Per-instance rate limiter for Yahoo Finance requests.

    Each instance maintains its own cooldown timer, request window,
    and failure counter — so background and live traffic are isolated.
    """

    def __init__(
        self,
        name: str,
        min_delay: float = 0.3,
        max_rpm: int = 30,
        cooldown_sec: int = 60,
        max_failures: int = 5,
        extended_sec: int = 300,
    ):
        self.name = name
        self._lock = threading.Lock()
        self._last_request_time = datetime.min
        self._request_count_window: list = []
        self._cooldown_until = None
        self._consecutive_failures = 0

        # Tunables
        self.MIN_DELAY_SECONDS = min_delay
        self.MAX_REQUESTS_PER_MINUTE = max_rpm
        self.COOLDOWN_DURATION_SECONDS = cooldown_sec
        self.MAX_CONSECUTIVE_FAILURES = max_failures
        self.EXTENDED_COOLDOWN_SECONDS = extended_sec

    # ── core methods ────────────────────────────────────────────

    def wait_if_needed(self) -> bool:
        """Wait if necessary before making a request. Returns True if OK to proceed."""
        with self._lock:
            now = datetime.utcnow()

            # Check cooldown
            if self._cooldown_until and now < self._cooldown_until:
                remaining = (self._cooldown_until - now).total_seconds()
                logger.warning(
                    f"[YFinance {self.name}] In cooldown. {remaining:.0f}s remaining."
                )
                return False

            # Clear expired cooldown
            if self._cooldown_until and now >= self._cooldown_until:
                self._cooldown_until = None
                self._consecutive_failures = 0
                logger.info(f"[YFinance {self.name}] Cooldown expired, resuming.")

            # Trim request window to last 60 s
            one_minute_ago = now - timedelta(minutes=1)
            self._request_count_window = [
                t for t in self._request_count_window if t > one_minute_ago
            ]

            # Per-minute cap
            if len(self._request_count_window) >= self.MAX_REQUESTS_PER_MINUTE:
                logger.warning(
                    f"[YFinance {self.name}] Rate limit reached "
                    f"({self.MAX_REQUESTS_PER_MINUTE}/min)"
                )
                return False

            # Enforce minimum delay
            time_since_last = (now - self._last_request_time).total_seconds()
            if time_since_last < self.MIN_DELAY_SECONDS:
                time.sleep(self.MIN_DELAY_SECONDS - time_since_last)

            # Record request
            self._last_request_time = datetime.utcnow()
            self._request_count_window.append(self._last_request_time)
            return True

    def report_success(self):
        """Report a successful request (resets failure counter)."""
        with self._lock:
            self._consecutive_failures = 0

    def report_rate_limit_error(self):
        """Report a 429 rate limit error (triggers cooldown)."""
        with self._lock:
            self._consecutive_failures += 1

            if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
                cooldown = self.EXTENDED_COOLDOWN_SECONDS
                logger.error(
                    f"[YFinance {self.name}] Too many failures "
                    f"({self._consecutive_failures}). Extended cooldown: {cooldown}s"
                )
            else:
                cooldown = self.COOLDOWN_DURATION_SECONDS
                logger.warning(
                    f"[YFinance {self.name}] Rate limit hit. Cooldown: {cooldown}s"
                )

            self._cooldown_until = datetime.utcnow() + timedelta(seconds=cooldown)

    def is_in_cooldown(self) -> bool:
        """Check if currently in cooldown period."""
        with self._lock:
            if self._cooldown_until is None:
                return False
            return datetime.utcnow() < self._cooldown_until

    def get_cooldown_remaining(self) -> float:
        """Get remaining cooldown time in seconds."""
        with self._lock:
            if self._cooldown_until is None:
                return 0
            return max(0, (self._cooldown_until - datetime.utcnow()).total_seconds())

    def reset(self):
        """Reset all state (useful for testing)."""
        with self._lock:
            self._last_request_time = datetime.min
            self._request_count_window = []
            self._cooldown_until = None
            self._consecutive_failures = 0


# ── Two independent buckets ─────────────────────────────────────
#
# 'live'       – serves real-time user requests; short cooldowns so
#                the UI recovers quickly even if Yahoo briefly 429s.
# 'background' – serves cron/batch jobs; longer cooldowns + lower
#                RPM so bulk syncs don't burn through the quota.

_live_limiter = YFinanceRateLimiter(
    name="live",
    max_rpm=120,  # Increased from 30 to allow dashboard parallelism
    cooldown_sec=10,  # Reduced from 30
    extended_sec=30,  # Reduced from 60
)

_background_limiter = YFinanceRateLimiter(
    name="background",
    max_rpm=60,  # Increased from 20
    cooldown_sec=60,
    extended_sec=120,
)


def _get_limiter(context: str = "live") -> YFinanceRateLimiter:
    return _background_limiter if context == "background" else _live_limiter


# ── Convenience functions (backward-compatible) ─────────────────
# Default context='live' keeps ALL existing handler call-sites
# working without any code changes.


def check_rate_limit(context: str = "live") -> bool:
    """Check if we can make a request. Returns True if OK."""
    return _get_limiter(context).wait_if_needed()


def report_yfinance_error(is_rate_limit: bool = False, context: str = "live"):
    """Report an error from yfinance."""
    if is_rate_limit:
        _get_limiter(context).report_rate_limit_error()


def report_yfinance_success(context: str = "live"):
    """Report successful yfinance call."""
    _get_limiter(context).report_success()


def is_in_cooldown(context: str = "live") -> bool:
    """Check if currently in cooldown period."""
    return _get_limiter(context).is_in_cooldown()
