"""
Crypto Data Handler - YFinance Integration
Functions for fetching cryptocurrency data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from . import get_yfinance_session

logger = logging.getLogger(__name__)


def get_crypto_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time crypto quote for a single symbol.
    
    Args:
        symbol: Crypto ticker symbol (e.g., 'BTC-USD')
    
    Returns:
        Dictionary with crypto quote data or None if error/not crypto
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        # Verify it's a crypto asset
        quote_type = info.get('quoteType')
        if quote_type != 'CRYPTOCURRENCY':
            logger.warning(f"{symbol} is not a cryptocurrency (type: {quote_type})")
            # We might still want to proceed if it's strictly requested as crypto, 
            # but strictly speaking we should filter. For now, let's allow but warn.
        
        if not info or 'symbol' not in info:
            return None
        
        return {
            'symbol': info.get('symbol', symbol),
            'name': info.get('shortName') or info.get('longName'),
            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
            'change': info.get('regularMarketChange'),
            'changePercent': info.get('regularMarketChangePercent'),
            'volume': info.get('regularMarketVolume') or info.get('volume'),
            'marketCap': info.get('marketCap'),
            'high52w': info.get('fiftyTwoWeekHigh'),
            'low52w': info.get('fiftyTwoWeekLow'),
            'previousClose': info.get('previousClose') or info.get('regularMarketPreviousClose'),
            'open': info.get('regularMarketOpen') or info.get('open'),
            'dayHigh': info.get('dayHigh') or info.get('regularMarketDayHigh'),
            'dayLow': info.get('dayLow') or info.get('regularMarketDayLow'),
            'avgVolume': info.get('averageVolume'),
            'circulatingSupply': info.get('circulatingSupply'),
            'totalSupply': info.get('totalSupply'),
            'maxSupply': info.get('maxSupply'),
            'currency': info.get('currency', 'USD'),
            'quoteType': 'CRYPTOCURRENCY',
            'description': info.get('description') or info.get('longBusinessSummary'),
            'logoUrl': info.get('logo_url'),
            # Mapper for unified MarketData model compatibility
            'sector': 'Cryptocurrency',
            'industry': 'Digital Assets',
            'exchange': 'CCC', # Common code for CryptoCompare or generic crypto
        }
    except Exception as e:
        logger.error(f"Error fetching crypto quote for {symbol}: {e}")
        return None


def get_crypto_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for a cryptocurrency.
    
    Args:
        symbol: Crypto ticker symbol
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    
    Returns:
        List of OHLCV dictionaries
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return []
        
        results = []
        for date, row in hist.iterrows():
            formatted_date = date.isoformat() if hasattr(date, 'isoformat') else str(date)
            results.append({
                'date': formatted_date,
                'open': float(row['Open']) if row['Open'] else None,
                'high': float(row['High']) if row['High'] else None,
                'low': float(row['Low']) if row['Low'] else None,
                'close': float(row['Close']) if row['Close'] else None,
                'volume': int(row['Volume']) if row['Volume'] else None,
            })
        return results
    except Exception as e:
        logger.error(f"Error fetching crypto history for {symbol}: {e}")
        return []


def import_crypto_to_db(symbol: str, db_session=None) -> bool:
    """
    Import crypto data to database.
    
    Args:
        symbol: Crypto ticker symbol
        db_session: SQLAlchemy session
        
    Returns:
        True if success, False otherwise
    """
    from models import db, MarketData
    
    session = db_session or db.session
    try:
        symbol = symbol.upper()
        quote = get_crypto_quote(symbol)
        if not quote:
            return False
            
        # Check if exists
        existing = MarketData.query.filter_by(
            symbol=symbol,
            asset_type='crypto',
            country_code='GLOBAL'
        ).first()
        
        if existing:
            # Update
            existing.name = quote.get('name')
            existing.price = quote.get('price')
            existing.change = quote.get('change')
            existing.change_percent = quote.get('changePercent')
            existing.volume = quote.get('volume')
            existing.market_cap = quote.get('marketCap')
            existing.high52w = quote.get('high52w')
            existing._52_week_high = quote.get('high52w') # db column name mapping
            existing._52_week_low = quote.get('low52w')
            existing.previous_close = quote.get('previousClose')
            existing.open_price = quote.get('open')
            existing.day_high = quote.get('dayHigh')
            existing.day_low = quote.get('dayLow')
            existing.avg_volume = quote.get('avgVolume')
            existing.description = quote.get('description')
            existing.last_updated = datetime.utcnow()
            # Store supply info in extra fields if available or map to strict columns
            existing.shares_outstanding = quote.get('circulatingSupply') 
        else:
            # Create
            new_crypto = MarketData(
                symbol=symbol,
                name=quote.get('name', symbol),
                price=quote.get('price', 0),
                change=quote.get('change', 0),
                change_percent=quote.get('changePercent', 0),
                volume=quote.get('volume'),
                market_cap=quote.get('marketCap'),
                _52_week_high=quote.get('high52w'),
                _52_week_low=quote.get('low52w'),
                previous_close=quote.get('previousClose'),
                open_price=quote.get('open'),
                day_high=quote.get('dayHigh'),
                day_low=quote.get('dayLow'),
                avg_volume=quote.get('avgVolume'),
                shares_outstanding=quote.get('circulatingSupply'),
                description=quote.get('description'),
                asset_type='crypto',
                country_code='GLOBAL',
                is_listed=True,
                sector='Cryptocurrency',
                industry='Digital Assets',
                currency='USD',
                last_updated=datetime.utcnow()
            )
            session.add(new_crypto)
            
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        logger.error(f"Error importing crypto {symbol}: {e}")
        return False


TOP_CRYPTOS = ['BTC-USD', 'ETH-USD', 'BNB-USD', 'XRP-USD', 'ADA-USD', 'DOGE-USD', 'SOL-USD', 'DOT-USD']

def get_multiple_crypto_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Get real-time quotes for multiple crypto symbols.
    Uses yf.Tickers for batch fetching (more efficient than individual calls).
    """
    from .rate_limiter import check_rate_limit, report_yfinance_error, report_yfinance_success
    
    results = []
    
    # Check rate limit before making request
    if not check_rate_limit():
        logger.warning("[Crypto Handler] Rate limited, returning empty list")
        return results
    
    try:
        session = get_yfinance_session()
        tickers = yf.Tickers(' '.join(symbols), session=session)
        
        for symbol in symbols:
            try:
                ticker = tickers.tickers.get(symbol.upper())
                if ticker:
                    info = ticker.info
                    if info and 'symbol' in info:
                        results.append({
                            'symbol': info.get('symbol', symbol),
                            'name': info.get('shortName') or info.get('longName'),
                            'price': info.get('currentPrice') or info.get('regularMarketPrice'),
                            'change': info.get('regularMarketChange'),
                            'changePercent': info.get('regularMarketChangePercent'),
                            'volume': info.get('regularMarketVolume') or info.get('volume'),
                            'marketCap': info.get('marketCap'),
                            'currency': info.get('currency', 'USD'),
                            'quoteType': 'CRYPTOCURRENCY',
                        })
            except Exception as e:
                error_msg = str(e)
                if 'Too Many Requests' in error_msg or '429' in error_msg:
                    report_yfinance_error(is_rate_limit=True)
                    break  # Stop processing, we're rate limited
                logger.warning(f"Error fetching {symbol}: {e}")
        
        if results:
            report_yfinance_success()
            logger.info(f"[Crypto Handler] Fetched {len(results)}/{len(symbols)} crypto quotes")
            
    except Exception as e:
        error_msg = str(e)
        if 'Too Many Requests' in error_msg or '429' in error_msg:
            report_yfinance_error(is_rate_limit=True)
        else:
            report_yfinance_error(is_rate_limit=False)
        logger.error(f"Error fetching multiple crypto quotes: {e}")
    
    return results



def import_cryptos_to_db(symbols: List[str], db_session=None) -> Dict[str, int]:
    """
    Import list of keys to DB. Wrapper around single import for now or bulk optimization.
    """
    imported = 0
    errors = 0
    
    for symbol in symbols:
        if import_crypto_to_db(symbol, db_session):
            imported += 1
        else:
            errors += 1
            
    return {'imported': imported, 'errors': errors}

