"""
Stock Data Handler - YFinance Integration
Functions for fetching stock data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def get_stock_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time stock quote for a single symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL')
    
    Returns:
        Dictionary with stock quote data or None if error
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
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
            'peRatio': info.get('trailingPE'),
            'forwardPe': info.get('forwardPE'),
            'eps': info.get('trailingEps'),
            'high52w': info.get('fiftyTwoWeekHigh'),
            'low52w': info.get('fiftyTwoWeekLow'),
            'previousClose': info.get('previousClose') or info.get('regularMarketPreviousClose'),
            'open': info.get('regularMarketOpen') or info.get('open'),
            'dayHigh': info.get('dayHigh') or info.get('regularMarketDayHigh'),
            'dayLow': info.get('dayLow') or info.get('regularMarketDayLow'),
            'avgVolume': info.get('averageVolume'),
            'beta': info.get('beta'),
            'dividendYield': info.get('dividendYield'),
            'dividendRate': info.get('dividendRate'),
            'bookValue': info.get('bookValue'),
            'priceToBook': info.get('priceToBook'),
            'sharesOutstanding': info.get('sharesOutstanding'),
            'floatShares': info.get('floatShares'),
            'shortRatio': info.get('shortRatio'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'exchange': info.get('exchange'),
            'currency': info.get('currency', 'USD'),
            'country': info.get('country'),
            'website': info.get('website'),
            'logoUrl': info.get('logo_url'),
            'description': info.get('longBusinessSummary'),
        }
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return None


def get_multiple_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Get real-time quotes for multiple stock symbols.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        List of dictionaries with stock quote data
    """
    results = []
    try:
        tickers = yf.Tickers(' '.join(symbols))
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
                            'peRatio': info.get('trailingPE'),
                            'high52w': info.get('fiftyTwoWeekHigh'),
                            'low52w': info.get('fiftyTwoWeekLow'),
                            'sector': info.get('sector'),
                            'industry': info.get('industry'),
                            'exchange': info.get('exchange'),
                            'currency': info.get('currency', 'USD'),
                        })
            except Exception as e:
                logger.warning(f"Error fetching {symbol}: {e}")
    except Exception as e:
        logger.error(f"Error fetching multiple quotes: {e}")
    
    return results


def get_stock_info(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get full company info including fundamentals.
    Same as get_stock_quote but with explicit naming.
    """
    return get_stock_quote(symbol)


def get_stock_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for a stock.
    
    Args:
        symbol: Stock ticker symbol
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    
    Returns:
        List of OHLCV dictionaries
    """
    try:
        ticker = yf.Ticker(symbol)
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
        logger.error(f"Error fetching history for {symbol}: {e}")
        return []


def get_recommendations(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get analyst recommendations for a stock.
    
    Returns:
        Dictionary with recommendation summary and recent upgrades/downgrades
    """
    try:
        ticker = yf.Ticker(symbol)
        
        result = {
            'symbol': symbol,
            'summary': None,
            'upgrades_downgrades': []
        }
        
        # Get recommendation summary
        try:
            rec_summary = ticker.recommendations_summary
            if rec_summary is not None and not rec_summary.empty:
                latest = rec_summary.iloc[0] if len(rec_summary) > 0 else None
                if latest is not None:
                    result['summary'] = {
                        'strongBuy': int(latest.get('strongBuy', 0)),
                        'buy': int(latest.get('buy', 0)),
                        'hold': int(latest.get('hold', 0)),
                        'sell': int(latest.get('sell', 0)),
                        'strongSell': int(latest.get('strongSell', 0)),
                    }
        except Exception as e:
            logger.warning(f"No recommendation summary for {symbol}: {e}")
        
        # Get upgrades/downgrades
        try:
            upgrades = ticker.upgrades_downgrades
            if upgrades is not None and not upgrades.empty:
                for date, row in upgrades.head(10).iterrows():
                    result['upgrades_downgrades'].append({
                        'date': date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date),
                        'firm': row.get('Firm'),
                        'toGrade': row.get('ToGrade'),
                        'fromGrade': row.get('FromGrade'),
                        'action': row.get('Action'),
                    })
        except Exception as e:
            logger.warning(f"No upgrades/downgrades for {symbol}: {e}")
        
        return result
    except Exception as e:
        logger.error(f"Error fetching recommendations for {symbol}: {e}")
        return None


def get_analyst_price_targets(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get analyst price targets for a stock.
    
    Returns:
        Dictionary with current, high, low, mean, median price targets
    """
    try:
        ticker = yf.Ticker(symbol)
        targets = ticker.analyst_price_targets
        
        if targets is None:
            return None
        
        return {
            'symbol': symbol,
            'current': targets.get('current'),
            'high': targets.get('high'),
            'low': targets.get('low'),
            'mean': targets.get('mean'),
            'median': targets.get('median'),
        }
    except Exception as e:
        logger.error(f"Error fetching price targets for {symbol}: {e}")
        return None


def import_stocks_to_db(symbols: List[str], db_session=None) -> Dict[str, int]:
    """
    Import stock data to database.
    
    Args:
        symbols: List of stock ticker symbols
        db_session: SQLAlchemy database session (optional, will import from models if not provided)
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, MarketData
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    for symbol in symbols:
        try:
            quote = get_stock_quote(symbol)
            if not quote:
                errors += 1
                continue
            
            # Check if exists
            existing = MarketData.query.filter_by(
                symbol=symbol.upper(),
                asset_type='stock'
            ).first()
            
            if existing:
                # Update existing record
                existing.name = quote.get('name')
                existing.price = quote.get('price')
                existing.change = quote.get('change')
                existing.change_percent = quote.get('changePercent')
                existing.volume = quote.get('volume')
                existing.market_cap = quote.get('marketCap')
                existing.pe_ratio = quote.get('peRatio')
                existing._52_week_high = quote.get('high52w')
                existing._52_week_low = quote.get('low52w')
                existing.previous_close = quote.get('previousClose')
                existing.open_price = quote.get('open')
                existing.day_high = quote.get('dayHigh')
                existing.day_low = quote.get('dayLow')
                existing.avg_volume = quote.get('avgVolume')
                existing.beta = quote.get('beta')
                existing.forward_pe = quote.get('forwardPe')
                existing.trailing_pe = quote.get('peRatio')
                existing.eps = quote.get('eps')
                existing.dividend_yield = quote.get('dividendYield')
                existing.dividend_rate = quote.get('dividendRate')
                existing.book_value = quote.get('bookValue')
                existing.price_to_book = quote.get('priceToBook')
                existing.shares_outstanding = quote.get('sharesOutstanding')
                existing.float_shares = quote.get('floatShares')
                existing.short_ratio = quote.get('shortRatio')
                existing.sector = quote.get('sector')
                existing.industry = quote.get('industry')
                existing.exchange = quote.get('exchange')
                existing.currency = quote.get('currency', 'USD')
                existing.website = quote.get('website')
                existing.logo_url = quote.get('logoUrl')
                existing.description = quote.get('description')
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                # Create new record
                new_stock = MarketData(
                    symbol=symbol.upper(),
                    name=quote.get('name'),
                    price=quote.get('price'),
                    change=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    volume=quote.get('volume'),
                    market_cap=quote.get('marketCap'),
                    pe_ratio=quote.get('peRatio'),
                    _52_week_high=quote.get('high52w'),
                    _52_week_low=quote.get('low52w'),
                    previous_close=quote.get('previousClose'),
                    open_price=quote.get('open'),
                    day_high=quote.get('dayHigh'),
                    day_low=quote.get('dayLow'),
                    avg_volume=quote.get('avgVolume'),
                    beta=quote.get('beta'),
                    forward_pe=quote.get('forwardPe'),
                    trailing_pe=quote.get('peRatio'),
                    eps=quote.get('eps'),
                    dividend_yield=quote.get('dividendYield'),
                    dividend_rate=quote.get('dividendRate'),
                    book_value=quote.get('bookValue'),
                    price_to_book=quote.get('priceToBook'),
                    shares_outstanding=quote.get('sharesOutstanding'),
                    float_shares=quote.get('floatShares'),
                    short_ratio=quote.get('shortRatio'),
                    sector=quote.get('sector'),
                    industry=quote.get('industry'),
                    exchange=quote.get('exchange'),
                    currency=quote.get('currency', 'USD'),
                    asset_type='stock',
                    website=quote.get('website'),
                    logo_url=quote.get('logoUrl'),
                    description=quote.get('description'),
                    last_updated=datetime.utcnow(),
                )
                session.add(new_stock)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing {symbol}: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(symbols)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}
