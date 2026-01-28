"""
Market Data Handlers - YFinance Integration
Unified interface for fetching market data from Yahoo Finance
"""

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

