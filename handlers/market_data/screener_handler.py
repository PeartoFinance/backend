"""
Screener Data Handler - YFinance Integration
Functions for screening stocks using predefined and custom queries
"""
import yfinance as yf
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Predefined screener queries available in yfinance
PREDEFINED_SCREENERS = [
    'aggressive_small_caps',
    'day_gainers',
    'day_losers',
    'growth_technology_stocks',
    'most_actives',
    'most_shorted_stocks',
    'small_cap_gainers',
    'undervalued_growth_stocks',
    'undervalued_large_caps',
    'conservative_foreign_funds',
    'high_yield_bond',
    'portfolio_anchors',
    'solid_large_growth_funds',
    'solid_midcap_growth_funds',
    'top_mutual_funds',
]


def run_predefined_screen(
    screener_name: str, 
    count: int = 25
) -> List[Dict[str, Any]]:
    """
    Run a predefined stock screener.
    
    Args:
        screener_name: Name of predefined screener (e.g., 'day_gainers')
        count: Number of results to return (max 250)
    
    Returns:
        List of stock dictionaries matching the screen
    """
    if screener_name not in PREDEFINED_SCREENERS:
        logger.warning(f"Unknown screener: {screener_name}")
        return []
    
    try:
        response = yf.screen(screener_name, count=min(count, 250))
        
        if response is None:
            return []
        
        quotes = response.get('quotes', [])
        
        results = []
        for quote in quotes:
            results.append({
                'symbol': quote.get('symbol'),
                'name': quote.get('shortName') or quote.get('longName'),
                'price': quote.get('regularMarketPrice'),
                'change': quote.get('regularMarketChange'),
                'changePercent': quote.get('regularMarketChangePercent'),
                'volume': quote.get('regularMarketVolume'),
                'marketCap': quote.get('marketCap'),
                'avgVolume50Day': quote.get('averageDailyVolume50Day'),
                'fiftyTwoWeekLow': quote.get('fiftyTwoWeekLow'),
                'fiftyTwoWeekHigh': quote.get('fiftyTwoWeekHigh'),
                'exchange': quote.get('exchange'),
                'sector': quote.get('sector'),
                'industry': quote.get('industry'),
            })
        
        return results
    except Exception as e:
        logger.error(f"Error running screener {screener_name}: {e}")
        return []


def get_day_gainers(limit: int = 25) -> List[Dict[str, Any]]:
    """Get top gaining stocks for the day."""
    return run_predefined_screen('day_gainers', limit)


def get_day_losers(limit: int = 25) -> List[Dict[str, Any]]:
    """Get top losing stocks for the day."""
    return run_predefined_screen('day_losers', limit)


def get_most_active(limit: int = 25) -> List[Dict[str, Any]]:
    """Get most actively traded stocks."""
    return run_predefined_screen('most_actives', limit)


def get_undervalued_growth(limit: int = 25) -> List[Dict[str, Any]]:
    """Get undervalued growth stocks."""
    return run_predefined_screen('undervalued_growth_stocks', limit)


def get_small_cap_gainers(limit: int = 25) -> List[Dict[str, Any]]:
    """Get top gaining small cap stocks."""
    return run_predefined_screen('small_cap_gainers', limit)


def get_tech_growth_stocks(limit: int = 25) -> List[Dict[str, Any]]:
    """Get growth technology stocks."""
    return run_predefined_screen('growth_technology_stocks', limit)


def run_custom_screen(
    query,
    sort_field: str = 'percentchange',
    sort_asc: bool = False,
    size: int = 100
) -> List[Dict[str, Any]]:
    """
    Run a custom stock screen using EquityQuery.
    
    Args:
        query: An EquityQuery object or dict representing the query
        sort_field: Field to sort by
        sort_asc: Sort ascending if True
        size: Number of results (max 250)
    
    Returns:
        List of stock dictionaries matching the screen
    
    Example:
        from yfinance import EquityQuery
        
        # Find US stocks with >3% daily change
        query = EquityQuery('and', [
            EquityQuery('gt', ['percentchange', 3]),
            EquityQuery('eq', ['region', 'us'])
        ])
        results = run_custom_screen(query)
    """
    try:
        response = yf.screen(
            query, 
            sortField=sort_field, 
            sortAsc=sort_asc, 
            size=min(size, 250)
        )
        
        if response is None:
            return []
        
        quotes = response.get('quotes', [])
        
        results = []
        for quote in quotes:
            results.append({
                'symbol': quote.get('symbol'),
                'name': quote.get('shortName') or quote.get('longName'),
                'price': quote.get('regularMarketPrice'),
                'change': quote.get('regularMarketChange'),
                'changePercent': quote.get('regularMarketChangePercent'),
                'volume': quote.get('regularMarketVolume'),
                'marketCap': quote.get('marketCap'),
                'exchange': quote.get('exchange'),
                'sector': quote.get('sector'),
                'industry': quote.get('industry'),
            })
        
        return results
    except Exception as e:
        logger.error(f"Error running custom screen: {e}")
        return []


def build_equity_query(
    region: str = None,
    sector: str = None,
    min_percent_change: float = None,
    max_percent_change: float = None,
    min_market_cap: int = None,
    max_market_cap: int = None,
    min_pe_ratio: float = None,
    max_pe_ratio: float = None,
) -> Any:
    """
    Build an EquityQuery from simple parameters.
    
    Args:
        region: Market region (e.g., 'us', 'gb', 'in')
        sector: Sector name (e.g., 'Technology', 'Healthcare')
        min_percent_change: Minimum percent change
        max_percent_change: Maximum percent change
        min_market_cap: Minimum market cap in USD
        max_market_cap: Maximum market cap in USD
        min_pe_ratio: Minimum P/E ratio
        max_pe_ratio: Maximum P/E ratio
    
    Returns:
        EquityQuery object
    """
    from yfinance import EquityQuery
    
    conditions = []
    
    if region:
        conditions.append(EquityQuery('eq', ['region', region]))
    
    if sector:
        conditions.append(EquityQuery('eq', ['sector', sector]))
    
    if min_percent_change is not None:
        conditions.append(EquityQuery('gt', ['percentchange', min_percent_change]))
    
    if max_percent_change is not None:
        conditions.append(EquityQuery('lt', ['percentchange', max_percent_change]))
    
    if min_market_cap is not None:
        conditions.append(EquityQuery('gt', ['intradaymarketcap', min_market_cap]))
    
    if max_market_cap is not None:
        conditions.append(EquityQuery('lt', ['intradaymarketcap', max_market_cap]))
    
    if min_pe_ratio is not None:
        conditions.append(EquityQuery('gt', ['peratio.lasttwelvemonths', min_pe_ratio]))
    
    if max_pe_ratio is not None:
        conditions.append(EquityQuery('lt', ['peratio.lasttwelvemonths', max_pe_ratio]))
    
    if not conditions:
        # Default: return all US stocks
        return EquityQuery('eq', ['region', 'us'])
    
    if len(conditions) == 1:
        return conditions[0]
    
    return EquityQuery('and', conditions)


def import_screener_to_db(
    screener_name: str,
    count: int = 50,
    db_session=None
) -> Dict[str, int]:
    """
    Import stocks from a screener to database.
    
    Args:
        screener_name: Name of predefined screener
        count: Number of stocks to import
        db_session: SQLAlchemy database session
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from .stock_handler import import_stocks_to_db
    
    stocks = run_predefined_screen(screener_name, count)
    
    if not stocks:
        return {'imported': 0, 'updated': 0, 'errors': 0, 'message': 'No stocks found'}
    
    symbols = [s['symbol'] for s in stocks if s.get('symbol')]
    
    return import_stocks_to_db(symbols, db_session)
