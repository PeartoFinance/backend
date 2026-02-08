"""
Forex Data Handler - YFinance Integration
Functions for fetching exchange rates from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from models import db, ForexRate
from . import get_yfinance_session

logger = logging.getLogger(__name__)

# Common currency pairs relative to USD
# Format: TargetCurrency (e.g., 'EUR') -> yfinance symbol (e.g., 'USDEUR=X')
COMMON_CURRENCIES = {
    'EUR': 'USDEUR=X',
    'GBP': 'USDGBP=X',
    'JPY': 'USDJPY=X',
    'CAD': 'USDCAD=X',
    'AUD': 'USDAUD=X',
    'CHF': 'USDCHF=X',
    'CNY': 'USDCNY=X',
    'INR': 'USDINR=X',
    'NPR': 'USDNPR=X',
    'AED': 'USDAED=X',
    'SAR': 'USDSAR=X',
    'SGD': 'USDSGD=X',
    'HKD': 'USDHKD=X',
}

def get_forex_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time forex quote for a single pair.
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        if not info or 'regularMarketPrice' not in info:
            # Fallback for some forex symbols where info might be sparse
            fast_info = ticker.fast_info
            if fast_info and 'last_price' in fast_info:
                return {
                    'symbol': symbol,
                    'price': fast_info['last_price'],
                    'change': 0, # fast_info doesn't easily provide change
                    'changePercent': 0,
                    'high': fast_info.get('day_high'),
                    'low': fast_info.get('day_low'),
                }
            return None
        
        return {
            'symbol': symbol,
            'price': info.get('regularMarketPrice') or info.get('currentPrice'),
            'change': info.get('regularMarketChange'),
            'changePercent': info.get('regularMarketChangePercent'),
            'high': info.get('dayHigh'),
            'low': info.get('dayLow'),
        }
    except Exception as e:
        logger.error(f"Error fetching forex quote for {symbol}: {e}")
        return None

def import_forex_to_db(currencies: List[str] = None) -> Dict[str, int]:
    """
    Import forex data to database.
    
    Args:
        currencies: List of target currency codes (e.g., ['EUR', 'NPR'])
                   If None, uses COMMON_CURRENCIES + any already in DB.
    """
    # 1. Start with our common list
    target_set = set(currencies or COMMON_CURRENCIES.keys())
    
    # 2. Add any currencies that already exist in our DB
    try:
        existing_currencies = db.session.query(ForexRate.target_currency).all()
        for (curr,) in existing_currencies:
            target_set.add(curr)
    except Exception as e:
        logger.warning(f"Could not fetch existing currencies from DB: {e}")

    updated = 0
    errors = 0
    
    for currency in target_set:
        try:
            currency = currency.upper()
            symbol = COMMON_CURRENCIES.get(currency) or f"USD{currency}=X"
            
            quote = get_forex_quote(symbol)
            if not quote:
                errors += 1
                continue
            
            # Check if exists
            existing = ForexRate.query.filter_by(
                base_currency='USD',
                target_currency=currency
            ).first()
            
            if existing:
                existing.rate = quote.get('price')
                existing.change = quote.get('change')
                existing.change_percent = quote.get('changePercent')
                existing.high = quote.get('high')
                existing.low = quote.get('low')
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                new_rate = ForexRate(
                    base_currency='USD',
                    target_currency=currency,
                    rate=quote.get('price'),
                    change=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    high=quote.get('high'),
                    low=quote.get('low'),
                    last_updated=datetime.utcnow()
                )
                db.session.add(new_rate)
                updated += 1
                
        except Exception as e:
            logger.error(f"Error importing forex {currency}: {e}")
            errors += 1
            
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing forex to database: {e}")
        return {'updated': 0, 'errors': len(target_list)}
        
    return {'updated': updated, 'errors': errors}


def get_forex_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for a forex pair.
    
    Args:
        symbol: Forex pair symbol (e.g., 'EURUSD')
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    
    Returns:
        List of OHLCV dictionaries
    """
    try:
        # Standardize symbol for Yahoo Finance (e.g. EURUSD -> EURUSD=X)
        # Note: Frontend usually sends 'EURUSD' or 'USDJPY' without =X
        yf_symbol = symbol.upper()
        if not yf_symbol.endswith('=X'):
             yf_symbol = f"{yf_symbol}=X"

        session = get_yfinance_session()
        ticker = yf.Ticker(yf_symbol, session=session)
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
                'volume': int(row['Volume']) if row['Volume'] else 0,
            })
        return results
    except Exception as e:
        logger.error(f"Error fetching forex history for {symbol}: {e}")
        return []
