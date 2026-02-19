
import os
import logging
import tempfile
import yfinance as yf

logger = logging.getLogger(__name__)

def patch_yfinance():
    """
    Configure yfinance to use a custom cache location and patch session
    to avoid 'SQLite driver not installed' errors and rate limits.
    """
    try:
        # 1. Set custom cache location to avoid default SQLite cache issues
        cache_dir = os.path.join(tempfile.gettempdir(), 'yf_cache')
        os.makedirs(cache_dir, exist_ok=True)
        yf.set_tz_cache_location(cache_dir)
        logger.info(f"[YFinance Patch] Set cache location to: {cache_dir}")
    except Exception as e:
        logger.warning(f"[YFinance Patch] Failed to set cache location: {e}")

    # 2. Add any other global yfinance configurations here if needed
    # Note: requests session patching happens in get_yfinance_session() 
    # but we want to ensure the global yfinance state is set early.

# Apply patch immediately on import
patch_yfinance()
