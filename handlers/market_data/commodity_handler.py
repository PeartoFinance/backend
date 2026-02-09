"""
Commodity Data Handler - YFinance Integration
Functions for fetching commodities futures data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from . import get_yfinance_session

logger = logging.getLogger(__name__)

# Major commodities with their Yahoo Finance futures symbols
COMMODITIES = {
    # Precious Metals
    'GC=F': {'name': 'Gold', 'unit': 'oz', 'category': 'metals'},
    'SI=F': {'name': 'Silver', 'unit': 'oz', 'category': 'metals'},
    'PL=F': {'name': 'Platinum', 'unit': 'oz', 'category': 'metals'},
    'PA=F': {'name': 'Palladium', 'unit': 'oz', 'category': 'metals'},
    'HG=F': {'name': 'Copper', 'unit': 'lb', 'category': 'metals'},
    # Energy
    'CL=F': {'name': 'Crude Oil WTI', 'unit': 'barrel', 'category': 'energy'},
    'BZ=F': {'name': 'Brent Crude', 'unit': 'barrel', 'category': 'energy'},
    'NG=F': {'name': 'Natural Gas', 'unit': 'MMBtu', 'category': 'energy'},
    'RB=F': {'name': 'RBOB Gasoline', 'unit': 'gallon', 'category': 'energy'},
    'HO=F': {'name': 'Heating Oil', 'unit': 'gallon', 'category': 'energy'},
    # Agriculture
    'ZC=F': {'name': 'Corn', 'unit': 'bushel', 'category': 'agriculture'},
    'ZW=F': {'name': 'Wheat', 'unit': 'bushel', 'category': 'agriculture'},
    'ZS=F': {'name': 'Soybeans', 'unit': 'bushel', 'category': 'agriculture'},
    'KC=F': {'name': 'Coffee', 'unit': 'lb', 'category': 'agriculture'},
    'SB=F': {'name': 'Sugar', 'unit': 'lb', 'category': 'agriculture'},
    'CC=F': {'name': 'Cocoa', 'unit': 'metric ton', 'category': 'agriculture'},
    'CT=F': {'name': 'Cotton', 'unit': 'lb', 'category': 'agriculture'},
    # Livestock
    'LE=F': {'name': 'Live Cattle', 'unit': 'lb', 'category': 'livestock'},
    'HE=F': {'name': 'Lean Hogs', 'unit': 'lb', 'category': 'livestock'},
}


def get_commodity_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time commodity quote.
    
    Args:
        symbol: Commodity futures ticker symbol (e.g., 'GC=F' for Gold)
    
    Returns:
        Dictionary with commodity quote data or None if error
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        if not info:
            return None
        
        commodity_info = COMMODITIES.get(symbol, {})
        
        return {
            'symbol': info.get('symbol', symbol),
            'name': commodity_info.get('name') or info.get('shortName') or info.get('longName'),
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
            'unit': commodity_info.get('unit', 'unit'),
            'category': commodity_info.get('category', 'other'),
            'currency': info.get('currency', 'USD'),
            'exchange': info.get('exchange'),
        }
    except Exception as e:
        logger.error(f"Error fetching commodity quote for {symbol}: {e}")
        return None


def get_all_commodities() -> List[Dict[str, Any]]:
    """
    Get quotes for all tracked commodities using BULK FETCH.
    Uses yf.download() to fetch all commodities in a single API call.
    
    Returns:
        List of commodity quote dictionaries
    """
    import pandas as pd
    from .rate_limiter import check_rate_limit, report_yfinance_error, report_yfinance_success
    
    symbols = list(COMMODITIES.keys())
    results = []
    
    # Check rate limit before making request
    if not check_rate_limit():
        logger.warning("[Commodity Handler] Rate limited, returning empty list")
        return results
    
    try:
        session = get_yfinance_session()
        
        # BULK DOWNLOAD - One API call for all commodities!
        data = yf.download(
            symbols,
            period='2d',
            interval='1d',
            group_by='ticker',
            progress=False,
            session=session,
            threads=False
        )
        
        if data.empty:
            logger.warning("[Commodity Handler] Bulk download returned empty data")
            report_yfinance_error(is_rate_limit=False)
            return results
        
        report_yfinance_success()
        
        # Process each symbol from the bulk data
        for symbol in symbols:
            try:
                commodity_info = COMMODITIES.get(symbol, {})
                
                if symbol not in data.columns.get_level_values(0):
                    continue
                
                symbol_data = data[symbol]
                
                if 'Close' not in symbol_data.columns or symbol_data['Close'].empty:
                    continue
                
                latest = symbol_data.iloc[-1]
                price = float(latest['Close']) if not pd.isna(latest['Close']) else None
                
                # Calculate change
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
                    'name': commodity_info.get('name', symbol),
                    'price': price,
                    'change': round(change, 4) if change else None,
                    'changePercent': round(change_percent, 2) if change_percent else None,
                    'previousClose': previous_close,
                    'dayHigh': float(latest['High']) if not pd.isna(latest.get('High')) else None,
                    'dayLow': float(latest['Low']) if not pd.isna(latest.get('Low')) else None,
                    'unit': commodity_info.get('unit'),
                    'category': commodity_info.get('category'),
                    'currency': 'USD',
                })
            except Exception as e:
                logger.warning(f"Error processing commodity {symbol} from bulk data: {e}")
                continue
        
        logger.info(f"[Commodity Handler] Bulk fetched {len(results)}/{len(symbols)} commodities")
        
    except Exception as e:
        error_msg = str(e)
        if 'Too Many Requests' in error_msg or '429' in error_msg:
            report_yfinance_error(is_rate_limit=True)
        else:
            report_yfinance_error(is_rate_limit=False)
        logger.error(f"Error in bulk commodity fetch: {e}")
    
    return results



def get_commodities_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get commodities filtered by category.
    
    Args:
        category: One of 'metals', 'energy', 'agriculture', 'livestock'
    
    Returns:
        List of commodity quote dictionaries
    """
    results = []
    
    for symbol, commodity_info in COMMODITIES.items():
        if commodity_info.get('category') == category:
            quote = get_commodity_quote(symbol)
            if quote:
                results.append(quote)
    
    return results


def get_commodity_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical data for a commodity.
    
    Args:
        symbol: Commodity futures ticker symbol
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
        logger.error(f"Error fetching commodity history for {symbol}: {e}")
        return []


def import_commodities_to_db(symbols: List[str] = None, db_session=None, country_code: str = 'GLOBAL') -> Dict[str, int]:
    """
    Import commodities to database.
    
    Args:
        symbols: List of commodity symbols (defaults to all COMMODITIES)
        db_session: SQLAlchemy database session
        country_code: Country code to assign (default: GLOBAL since commodities are global)
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, CommodityData
    
    if symbols is None:
        symbols = list(COMMODITIES.keys())
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    for symbol in symbols:
        try:
            quote = get_commodity_quote(symbol)
            if not quote:
                errors += 1
                continue
            
            # Check if exists
            existing = CommodityData.query.filter_by(symbol=symbol).first()
            
            if existing:
                # Update existing record
                existing.name = quote.get('name')
                existing.price = quote.get('price')
                existing.change = quote.get('change')
                existing.change_percent = quote.get('changePercent')
                existing.day_high = quote.get('dayHigh')
                existing.day_low = quote.get('dayLow')
                existing.year_high = quote.get('yearHigh')
                existing.year_low = quote.get('yearLow')
                existing.unit = quote.get('unit')
                existing.currency = quote.get('currency', 'USD')
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                # Create new record
                new_commodity = CommodityData(
                    symbol=symbol,
                    name=quote.get('name'),
                    price=quote.get('price'),
                    change=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    day_high=quote.get('dayHigh'),
                    day_low=quote.get('dayLow'),
                    year_high=quote.get('yearHigh'),
                    year_low=quote.get('yearLow'),
                    unit=quote.get('unit'),
                    currency=quote.get('currency', 'USD'),
                    country_code=country_code,
                    last_updated=datetime.utcnow(),
                )
                session.add(new_commodity)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing commodity {symbol}: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing commodities to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(symbols)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}
