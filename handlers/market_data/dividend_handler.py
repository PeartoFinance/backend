"""
Dividend Data Handler - YFinance Integration
Functions for fetching dividend data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
import pandas as pd
from . import get_yfinance_session

logger = logging.getLogger(__name__)


def get_stock_dividends(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get dividend history and info for a stock.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Dictionary with dividend data or None if error
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        
        # Get dividend history
        dividends = ticker.dividends
        
        dividend_data = {
            'symbol': symbol,
            'companyName': info.get('shortName') or info.get('longName'),
            'dividendYield': info.get('dividendYield'),
            'dividendRate': info.get('dividendRate'),
            'exDividendDate': None,
            'payoutRatio': info.get('payoutRatio'),
            'fiveYearAvgDividendYield': info.get('fiveYearAvgDividendYield'),
            'trailingAnnualDividendYield': info.get('trailingAnnualDividendYield'),
            'trailingAnnualDividendRate': info.get('trailingAnnualDividendRate'),
            'lastDividendValue': None,
            'lastDividendDate': None,
            'recentDividends': []
        }
        
        # Parse ex-dividend date
        ex_div_ts = info.get('exDividendDate')
        if ex_div_ts:
            try:
                dividend_data['exDividendDate'] = datetime.fromtimestamp(ex_div_ts).date().isoformat()
            except:
                pass
        
        # Get last dividend value and date  
        dividend_data['lastDividendValue'] = info.get('lastDividendValue')
        last_div_ts = info.get('lastDividendDate')
        if last_div_ts:
            try:
                dividend_data['lastDividendDate'] = datetime.fromtimestamp(last_div_ts).date().isoformat()
            except:
                pass
        
        # Get recent dividends from history
        if dividends is not None and len(dividends) > 0:
            recent = dividends.tail(10)
            dividend_data['recentDividends'] = [
                {
                    'date': d.isoformat() if hasattr(d, 'isoformat') else str(d),
                    'amount': float(v)
                }
                for d, v in zip(recent.index, recent.values)
            ]
        
        return dividend_data
        
    except Exception as e:
        logger.error(f"Error fetching dividends for {symbol}: {e}")
        return None


def get_ex_dividend_calendar() -> List[Dict[str, Any]]:
    """
    Get upcoming ex-dividend dates from popular dividend stocks.
    
    Returns:
        List of stocks with upcoming ex-dividend dates
    """
    # Popular dividend stocks to check
    dividend_stocks = [
        'AAPL', 'MSFT', 'JNJ', 'PG', 'KO', 'PEP', 'XOM', 'CVX', 'T', 'VZ',
        'IBM', 'MMM', 'MCD', 'WMT', 'HD', 'JPM', 'BAC', 'WFC', 'C', 'GS',
        'ABBV', 'MRK', 'PFE', 'LMT', 'RTX', 'BA', 'CAT', 'DE', 'UNP', 'UPS'
    ]
    
    upcoming = []
    today = datetime.now().date()
    
    for symbol in dividend_stocks:
        try:
            session = get_yfinance_session()
            ticker = yf.Ticker(symbol, session=session)
            info = ticker.info
            
            ex_div_ts = info.get('exDividendDate')
            if ex_div_ts:
                ex_div_date = datetime.fromtimestamp(ex_div_ts).date()
                
                # Include if ex-dividend date is in the future or within last 30 days
                if ex_div_date >= today - timedelta(days=30):
                    upcoming.append({
                        'symbol': symbol,
                        'companyName': info.get('shortName') or info.get('longName'),
                        'exDividendDate': ex_div_date.isoformat(),
                        'dividendYield': info.get('dividendYield'),
                        'dividendRate': info.get('dividendRate'),
                        'lastDividendValue': info.get('lastDividendValue'),
                    })
        except Exception as e:
            logger.warning(f"Error checking ex-dividend for {symbol}: {e}")
            continue
    
    # Sort by ex-dividend date
    upcoming.sort(key=lambda x: x.get('exDividendDate', ''))
    return upcoming


def import_dividends_to_db(symbols: List[str]) -> Dict[str, int]:
    """
    Import dividend data for symbols into database.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        Dictionary with import statistics
    """
    from models import db, Dividend
    
    imported = 0
    updated = 0
    errors = 0
    
    for symbol in symbols:
        try:
            session = get_yfinance_session()
            ticker = yf.Ticker(symbol.upper(), session=session)
            info = ticker.info
            
            if not info or not info.get('symbol'):
                errors += 1
                continue
            
            # Get dividend info
            dividend_yield = info.get('dividendYield')
            dividend_rate = info.get('dividendRate')
            
            # Skip if stock doesn't pay dividends
            if not dividend_rate and not dividend_yield:
                continue
            
            # Check for existing
            existing = Dividend.query.filter_by(symbol=symbol.upper()).first()
            
            # Parse ex-dividend date
            ex_div_date = None
            ex_div_ts = info.get('exDividendDate')
            if ex_div_ts:
                try:
                    ex_div_date = datetime.fromtimestamp(ex_div_ts).date()
                except:
                    pass
            
            # Parse last dividend date
            payment_date = None
            last_div_ts = info.get('lastDividendDate')
            if last_div_ts:
                try:
                    payment_date = datetime.fromtimestamp(last_div_ts).date()
                except:
                    pass
            
            # Calculate percentage (assuming dividend rate is annual)
            total_percent = (dividend_yield or 0) * 100 if dividend_yield else None
            
            if existing:
                existing.company_name = info.get('shortName') or info.get('longName')
                existing.dividend_amount = dividend_rate
                existing.total_percent = total_percent
                existing.cash_percent = total_percent  # Assuming cash dividend
                existing.ex_dividend_date = ex_div_date
                existing.payment_date = payment_date
                existing.status = 'approved'
                updated += 1
            else:
                div = Dividend(
                    symbol=symbol.upper(),
                    company_name=info.get('shortName') or info.get('longName'),
                    dividend_type='cash',
                    cash_percent=total_percent,
                    bonus_percent=0,
                    total_percent=total_percent,
                    dividend_amount=dividend_rate,
                    ex_dividend_date=ex_div_date,
                    payment_date=payment_date,
                    status='approved',
                    country_code='US'
                )
                db.session.add(div)
                imported += 1
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error importing dividend for {symbol}: {e}")
            db.session.rollback()
            errors += 1
    
    return {
        'imported': imported,
        'updated': updated,
        'errors': errors
    }


# Popular dividend-paying stocks for quick import
DIVIDEND_STOCKS = [
    # Dividend Aristocrats (25+ years of dividend increases)
    'KO', 'JNJ', 'PG', 'MMM', 'PEP', 'WMT', 'MCD', 'CL', 'XOM', 'CVX',
    'IBM', 'T', 'VZ', 'ABBV', 'MRK', 'PFE', 'CAT', 'EMR', 'SHW', 'GD',
    # High-yield dividend stocks
    'MO', 'PM', 'BTI', 'VZ', 'INTC', 'WBA', 'LYB', 'OKE', 'KMI', 'EPD',
    # Tech dividends
    'AAPL', 'MSFT', 'CSCO', 'TXN', 'AVGO', 'QCOM', 'INTC', 'HPQ', 'ORCL',
    # Financial dividends
    'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS', 'USB', 'PNC', 'TFC', 'KEY'
]
