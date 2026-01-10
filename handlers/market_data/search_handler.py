"""
Search Data Handler - YFinance Integration
Functions for searching tickers and looking up symbols
"""
import yfinance as yf
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def search_tickers(
    query: str, 
    max_results: int = 10,
    news_count: int = 0,
    enable_fuzzy: bool = True
) -> Dict[str, Any]:
    """
    Search for tickers by name or symbol.
    
    Args:
        query: Search query (ticker symbol or company name)
        max_results: Maximum number of stock quotes to return
        news_count: Number of news articles to include
        enable_fuzzy: Enable fuzzy search for typos
    
    Returns:
        Dictionary with quotes and optional news
    """
    try:
        search = yf.Search(
            query, 
            max_results=min(max_results, 20),
            news_count=news_count,
            enable_fuzzy_query=enable_fuzzy
        )
        
        result = {
            'quotes': [],
            'news': [],
            'query': query,
        }
        
        # Get quotes
        if search.quotes:
            for quote in search.quotes:
                result['quotes'].append({
                    'symbol': quote.get('symbol'),
                    'name': quote.get('shortname') or quote.get('longname'),
                    'exchange': quote.get('exchange'),
                    'exchangeDisplay': quote.get('exchDisp'),
                    'type': quote.get('quoteType'),
                    'typeDisplay': quote.get('typeDisp'),
                    'sector': quote.get('sector'),
                    'industry': quote.get('industry'),
                    'isYahooFinance': quote.get('isYahooFinance'),
                })
        
        # Get news if requested
        if news_count > 0 and search.news:
            for article in search.news:
                result['news'].append({
                    'title': article.get('title'),
                    'publisher': article.get('publisher'),
                    'link': article.get('link'),
                    'publishTime': article.get('providerPublishTime'),
                    'type': article.get('type'),
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url'),
                })
        
        return result
    except Exception as e:
        logger.error(f"Error searching for '{query}': {e}")
        return {'quotes': [], 'news': [], 'query': query, 'error': str(e)}


def lookup_ticker(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Look up a specific ticker symbol.
    
    Args:
        symbol: Ticker symbol to look up
    
    Returns:
        Dictionary with ticker info or None if not found
    """
    try:
        result = search_tickers(symbol, max_results=1)
        quotes = result.get('quotes', [])
        
        if quotes:
            return quotes[0]
        return None
    except Exception as e:
        logger.error(f"Error looking up ticker {symbol}: {e}")
        return None


def get_related_tickers(symbol: str, max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Get tickers related to a symbol (same sector/industry).
    
    Args:
        symbol: Ticker symbol to find related tickers for
        max_results: Maximum number of related tickers
    
    Returns:
        List of related ticker dictionaries
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info:
            return []
        
        # Search for tickers in same industry
        industry = info.get('industry')
        sector = info.get('sector')
        
        if industry:
            result = search_tickers(industry, max_results=max_results + 1)
            quotes = result.get('quotes', [])
            # Filter out the original symbol
            return [q for q in quotes if q.get('symbol') != symbol.upper()][:max_results]
        elif sector:
            result = search_tickers(sector, max_results=max_results + 1)
            quotes = result.get('quotes', [])
            return [q for q in quotes if q.get('symbol') != symbol.upper()][:max_results]
        
        return []
    except Exception as e:
        logger.error(f"Error getting related tickers for {symbol}: {e}")
        return []


def validate_symbol(symbol: str) -> bool:
    """
    Check if a ticker symbol is valid.
    
    Args:
        symbol: Ticker symbol to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Check if we got valid info
        if info and info.get('symbol'):
            return True
        return False
    except Exception:
        return False


def get_ticker_type(symbol: str) -> Optional[str]:
    """
    Get the type of a ticker (stock, ETF, crypto, index, etc.).
    
    Args:
        symbol: Ticker symbol
    
    Returns:
        Ticker type string or None if unknown
    """
    try:
        result = lookup_ticker(symbol)
        if result:
            return result.get('type') or result.get('typeDisplay')
        return None
    except Exception:
        return None
