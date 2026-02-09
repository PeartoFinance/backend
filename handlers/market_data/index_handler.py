"""
Index Data Handler - YFinance Integration
Functions for fetching market indices data from Yahoo Finance
"""
import yfinance as yf
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from . import get_yfinance_session


logger = logging.getLogger(__name__)

# Major world market indices with their Yahoo Finance symbols
MAJOR_INDICES = {
    # US Indices
    '^GSPC': 'S&P 500',
    '^DJI': 'Dow Jones Industrial Average',
    '^IXIC': 'NASDAQ Composite',
    '^RUT': 'Russell 2000',
    '^VIX': 'CBOE Volatility Index',
    '^NYA': 'NYSE Composite',
    '^NDX': 'NASDAQ 100',
    # European Indices
    '^FTSE': 'FTSE 100',
    '^GDAXI': 'DAX',
    '^FCHI': 'CAC 40',
    '^STOXX50E': 'EURO STOXX 50',
    '^IBEX': 'IBEX 35',
    # Asian Indices
    '^N225': 'Nikkei 225',
    '^HSI': 'Hang Seng',
    '000001.SS': 'Shanghai Composite',
    '^KS11': 'KOSPI',
    '^TWII': 'Taiwan Weighted',
    '^BSESN': 'BSE SENSEX',
    '^NSEI': 'NIFTY 50',
    # Other
    '^GSPTSE': 'S&P/TSX Composite',
    '^AXJO': 'S&P/ASX 200',
}


def get_index_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time market index quote.
    
    Args:
        symbol: Index ticker symbol (e.g., '^GSPC' for S&P 500)
    
    Returns:
        Dictionary with index quote data or None if error
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        if not info:
            return None
        
        return {
            'symbol': info.get('symbol', symbol),
            'name': info.get('shortName') or info.get('longName') or MAJOR_INDICES.get(symbol, symbol),
            'price': info.get('regularMarketPrice'),
            'change': info.get('regularMarketChange'),
            'changePercent': info.get('regularMarketChangePercent'),
            'previousClose': info.get('previousClose') or info.get('regularMarketPreviousClose'),
            'open': info.get('regularMarketOpen') or info.get('open'),
            'dayHigh': info.get('dayHigh') or info.get('regularMarketDayHigh'),
            'dayLow': info.get('dayLow') or info.get('regularMarketDayLow'),
            'yearHigh': info.get('fiftyTwoWeekHigh'),
            'yearLow': info.get('fiftyTwoWeekLow'),
            'volume': info.get('regularMarketVolume'),
            'exchange': info.get('exchange'),
            'currency': info.get('currency', 'USD'),
        }
    except Exception as e:
        logger.error(f"Error fetching index quote for {symbol}: {e}")
        return None


def get_all_major_indices() -> List[Dict[str, Any]]:
    """
    Get quotes for all major world indices using BULK FETCH.
    Uses yf.download() to fetch all indices in a single API call instead of 20+ individual calls.
    
    Returns:
        List of index quote dictionaries
    """
    from .rate_limiter import check_rate_limit, report_yfinance_error, report_yfinance_success
    
    symbols = list(MAJOR_INDICES.keys())
    results = []
    
    # Check rate limit before making request
    if not check_rate_limit():
        logger.warning("[Index Handler] Rate limited, returning empty list")
        return results
    
    try:
        session = get_yfinance_session()
        
        # BULK DOWNLOAD - One API call for all indices!
        # Get last 2 days to calculate change
        data = yf.download(
            symbols,
            period='2d',
            interval='1d',
            group_by='ticker',
            progress=False,
            session=session,
            threads=False  # Avoid threading issues
        )
        
        if data.empty:
            logger.warning("[Index Handler] Bulk download returned empty data")
            report_yfinance_error(is_rate_limit=False)
            return results
        
        report_yfinance_success()
        
        # Process each symbol from the bulk data
        for symbol in symbols:
            try:
                if symbol not in data.columns.get_level_values(0):
                    continue
                
                symbol_data = data[symbol]
                
                # Get latest values
                if 'Close' not in symbol_data.columns or symbol_data['Close'].empty:
                    continue
                
                latest = symbol_data.iloc[-1]
                price = float(latest['Close']) if not pd.isna(latest['Close']) else None
                
                # Calculate change from previous close
                change = None
                change_percent = None
                previous_close = None
                
                if len(symbol_data) >= 2:
                    prev = symbol_data.iloc[-2]
                    previous_close = float(prev['Close']) if not pd.isna(prev['Close']) else None
                    if previous_close and price:
                        change = price - previous_close
                        change_percent = (change / previous_close) * 100
                
                results.append({
                    'symbol': symbol,
                    'name': MAJOR_INDICES.get(symbol, symbol),
                    'displayName': MAJOR_INDICES.get(symbol, symbol),
                    'price': price,
                    'change': round(change, 4) if change else None,
                    'changePercent': round(change_percent, 2) if change_percent else None,
                    'previousClose': previous_close,
                    'dayHigh': float(latest['High']) if not pd.isna(latest.get('High')) else None,
                    'dayLow': float(latest['Low']) if not pd.isna(latest.get('Low')) else None,
                    'volume': int(latest['Volume']) if not pd.isna(latest.get('Volume')) else None,
                    'currency': 'USD',
                })
            except Exception as e:
                logger.warning(f"Error processing index {symbol} from bulk data: {e}")
                continue
        
        logger.info(f"[Index Handler] Bulk fetched {len(results)}/{len(symbols)} indices")
        
    except Exception as e:
        error_msg = str(e)
        if 'Too Many Requests' in error_msg or '429' in error_msg:
            report_yfinance_error(is_rate_limit=True)
        else:
            report_yfinance_error(is_rate_limit=False)
        logger.error(f"Error in bulk index fetch: {e}")
    
    return results



def get_us_indices() -> List[Dict[str, Any]]:
    """Get quotes for US market indices only."""
    us_symbols = ['^GSPC', '^DJI', '^IXIC', '^RUT', '^VIX', '^NYA', '^NDX']
    results = []
    
    for symbol in us_symbols:
        quote = get_index_quote(symbol)
        if quote:
            quote['displayName'] = MAJOR_INDICES.get(symbol, symbol)
            results.append(quote)
    
    return results


def get_index_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical data for a market index.
    
    Args:
        symbol: Index ticker symbol
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Valid intervals: 1d, 5d, 1wk, 1mo, 3mo
    
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
            results.append({
                'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                'open': float(row['Open']) if row['Open'] else None,
                'high': float(row['High']) if row['High'] else None,
                'low': float(row['Low']) if row['Low'] else None,
                'close': float(row['Close']) if row['Close'] else None,
                'volume': int(row['Volume']) if row['Volume'] else None,
            })
        return results
    except Exception as e:
        logger.error(f"Error fetching index history for {symbol}: {e}")
        return []


def import_indices_to_db(symbols: List[str] = None, db_session=None, country_code: str = None) -> Dict[str, int]:
    """
    Import market indices to database.
    
    Args:
        symbols: List of index symbols (defaults to MAJOR_INDICES)
        db_session: SQLAlchemy database session
        country_code: Country code to assign (if None, auto-detect from symbol)
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, MarketIndices
    
    if symbols is None:
        symbols = list(MAJOR_INDICES.keys())
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    for symbol in symbols:
        try:
            quote = get_index_quote(symbol)
            if not quote:
                errors += 1
                continue
            
            # Check if exists
            existing = MarketIndices.query.filter_by(symbol=symbol).first()
            
            if existing:
                # Update existing record
                existing.name = quote.get('name') or MAJOR_INDICES.get(symbol, symbol)
                existing.price = quote.get('price')
                existing.change_amount = quote.get('change')
                existing.change_percent = quote.get('changePercent')
                existing.previous_close = quote.get('previousClose')
                existing.day_high = quote.get('dayHigh')
                existing.day_low = quote.get('dayLow')
                existing.year_high = quote.get('yearHigh')
                existing.year_low = quote.get('yearLow')
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                # Create new record
                new_index = MarketIndices(
                    symbol=symbol,
                    name=quote.get('name') or MAJOR_INDICES.get(symbol, symbol),
                    price=quote.get('price'),
                    change_amount=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    previous_close=quote.get('previousClose'),
                    day_high=quote.get('dayHigh'),
                    day_low=quote.get('dayLow'),
                    year_high=quote.get('yearHigh'),
                    year_low=quote.get('yearLow'),
                    market_status='closed',
                    country_code=country_code or ('US' if symbol.startswith('^') else 'GLOBAL'),
                    last_updated=datetime.utcnow(),
                )
                session.add(new_index)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing index {symbol}: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing indices to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(symbols)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}
