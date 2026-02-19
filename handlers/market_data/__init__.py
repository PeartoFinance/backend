"""
Market Data Handlers - YFinance Integration
Unified interface for fetching market data from Yahoo Finance
"""
import logging

# Centralized session factory to bypass Yahoo rate limits
# Uses curl_cffi to impersonate Chrome's TLS fingerprint
_yfinance_session = None

def get_yfinance_session():
    """
    Get a session that impersonates Chrome to bypass Yahoo rate limits.
    Uses curl_cffi which mimics Chrome's TLS fingerprint.
    Falls back to standard requests if curl_cffi fails.
    """
    global _yfinance_session
    if _yfinance_session is None:
        try:
            # Force yfinance to use a custom cache location to avoid permission/driver issues
            import yfinance as yf
            import os
            import tempfile
            
            try:
                cache_dir = os.path.join(tempfile.gettempdir(), 'yf_cache')
                os.makedirs(cache_dir, exist_ok=True)
                yf.set_tz_cache_location(cache_dir)
            except Exception as e:
                logging.warning(f"[YFinance] Could not set custom cache location: {e}")

            from curl_cffi import requests as curl_requests
            _yfinance_session = curl_requests.Session(impersonate="chrome")
            _yfinance_session._is_curl_cffi = True
            
            # ENFORCE TIMEOUT: Monkey-patch the request method to ensure timeout
            original_request = _yfinance_session.request
            def timeout_request(*args, **kwargs):
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = 5  # 5 seconds timeout
                return original_request(*args, **kwargs)
            _yfinance_session.request = timeout_request
            
            logging.info("[YFinance] Using curl_cffi Chrome-impersonating session with 5s timeout")
        except ImportError:
            logging.warning("[YFinance] curl_cffi not installed, using default requests")
            import requests
            _yfinance_session = requests.Session()
            _yfinance_session._is_curl_cffi = False
            
            # ENFORCE TIMEOUT for standard requests
            original_request = _yfinance_session.request
            def timeout_request(*args, **kwargs):
                if 'timeout' not in kwargs:
                    kwargs['timeout'] = 5  # 5 seconds timeout
                return original_request(*args, **kwargs)
            _yfinance_session.request = timeout_request
    return _yfinance_session


def reset_yfinance_session():
    """
    Reset the session (call this if you encounter curl_cffi errors).
    This will force the next get_yfinance_session() to create a new session,
    and if curl_cffi fails, it will fall back to standard requests.
    """
    global _yfinance_session
    _yfinance_session = None
    logging.info("[YFinance] Session reset")


def get_fallback_session():
    """
    Get a standard requests session as fallback when curl_cffi fails.
    This should be used when curl_cffi throws DNS or threading errors.
    """
    import requests
    session = requests.Session()
    session._is_curl_cffi = False
    logging.warning("[YFinance] Using fallback requests session due to curl_cffi error")
    return session



from .stock_handler import (
    get_stock_quote,
    get_multiple_quotes,
    get_stock_info,
    get_stock_history,
    import_stocks_to_db,
    get_recommendations,
    get_analyst_price_targets,
)

from .crypto_handler import (
    get_crypto_quote,
    get_multiple_crypto_quotes,
    import_cryptos_to_db,
    import_crypto_to_db,
    get_crypto_history,
    TOP_CRYPTOS,
)

from .index_handler import (
    get_index_quote,
    get_all_major_indices,
    import_indices_to_db,
    MAJOR_INDICES,
)

from .commodity_handler import (
    get_commodity_quote,
    get_all_commodities,
    import_commodities_to_db,
    COMMODITIES,
)

from .calendar_handler import (
    get_earnings_calendar,
    get_ipo_calendar,
    get_splits_calendar,
    get_economic_events,
    import_earnings_to_db,
    import_ipos_to_db,
)

from .screener_handler import (
    get_day_gainers,
    get_day_losers,
    get_most_active,
    run_predefined_screen,
    run_custom_screen,
    PREDEFINED_SCREENERS,
)

from .search_handler import (
    search_tickers,
)

from .dividend_handler import (
    get_stock_dividends,
    get_ex_dividend_calendar,
    import_dividends_to_db,
    DIVIDEND_STOCKS,
)

from .news_notification_handler import (
    process_news_notifications,
    send_user_notification,
)

from .news_fetch_handler import (
    fetch_recent_news,
    match_news_to_user_preferences,
)

__all__ = [
    # Stock
    'get_stock_quote',
    'get_multiple_quotes',
    'get_stock_info',
    'get_stock_history',
    'import_stocks_to_db',
    'get_recommendations',
    'get_analyst_price_targets',
    # Crypto
    'get_crypto_quote',
    'get_multiple_crypto_quotes',
    'import_cryptos_to_db',
    'import_crypto_to_db',
    'get_crypto_history',
    'TOP_CRYPTOS',
    # Index
    'get_index_quote',
    'get_all_major_indices',
    'import_indices_to_db',
    'MAJOR_INDICES',
    # Commodity
    'get_commodity_quote',
    'get_all_commodities',
    'import_commodities_to_db',
    'COMMODITIES',
    # Calendar
    'get_earnings_calendar',
    'get_ipo_calendar',
    'get_splits_calendar',
    'get_economic_events',
    'import_earnings_to_db',
    'import_ipos_to_db',
    # Screener
    'get_day_gainers',
    'get_day_losers',
    'get_most_active',
    'run_predefined_screen',
    'run_custom_screen',
    'PREDEFINED_SCREENERS',
    # Search
    'search_tickers',
    # Dividend
    'get_stock_dividends',
    'get_ex_dividend_calendar',
    'import_dividends_to_db',
    'DIVIDEND_STOCKS',
    # news fetch
    'fetch_recent_news',
    'match_news_to_user_preferences',
    # news notification
    'process_news_notifications',
    'send_user_notification',
]

