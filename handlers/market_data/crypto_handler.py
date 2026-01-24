"""
Crypto Data Handler - YFinance Integration
Functions for fetching cryptocurrency data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

# Top cryptocurrencies with their Yahoo Finance symbols (format: SYMBOL-USD)
TOP_CRYPTOS = [
    'BTC-USD',   # Bitcoin
    'ETH-USD',   # Ethereum
    'BNB-USD',   # Binance Coin
    'XRP-USD',   # Ripple
    'SOL-USD',   # Solana
    'ADA-USD',   # Cardano
    'DOGE-USD',  # Dogecoin
    'AVAX-USD',  # Avalanche
    'DOT-USD',   # Polkadot
    'MATIC-USD', # Polygon
    'SHIB-USD',  # Shiba Inu
    'LTC-USD',   # Litecoin
    'TRX-USD',   # TRON
    'ATOM-USD',  # Cosmos
    'LINK-USD',  # Chainlink
    'UNI-USD',   # Uniswap
    'XLM-USD',   # Stellar
    'BCH-USD',   # Bitcoin Cash
    'ETC-USD',   # Ethereum Classic
    'FIL-USD',   # Filecoin
]


def get_crypto_quote(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get real-time cryptocurrency quote.
    
    Args:
        symbol: Crypto ticker symbol (e.g., 'BTC-USD' or 'BTC')
    
    Returns:
        Dictionary with crypto quote data or None if error
    """
    # Ensure symbol has -USD suffix
    if not symbol.endswith('-USD'):
        symbol = f"{symbol}-USD"
    
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or 'symbol' not in info:
            return None
        
        return {
            'symbol': info.get('symbol', symbol),
            'name': info.get('shortName') or info.get('name') or info.get('longName'),
            'price': info.get('regularMarketPrice'),
            'change': info.get('regularMarketChange'),
            'changePercent': info.get('regularMarketChangePercent'),
            'volume': info.get('regularMarketVolume') or info.get('volume24Hr'),
            'marketCap': info.get('marketCap'),
            'circulatingSupply': info.get('circulatingSupply'),
            'totalSupply': info.get('totalSupply'),
            'maxSupply': info.get('maxSupply'),
            'high52w': info.get('fiftyTwoWeekHigh'),
            'low52w': info.get('fiftyTwoWeekLow'),
            'previousClose': info.get('previousClose') or info.get('regularMarketPreviousClose'),
            'open': info.get('regularMarketOpen') or info.get('open'),
            'dayHigh': info.get('dayHigh') or info.get('regularMarketDayHigh'),
            'dayLow': info.get('dayLow') or info.get('regularMarketDayLow'),
            'avgVolume': info.get('averageVolume'),
            'currency': 'USD',
            'exchange': info.get('exchange'),
        }
    except Exception as e:
        logger.error(f"Error fetching crypto quote for {symbol}: {e}")
        return None


def get_multiple_crypto_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Get real-time quotes for multiple cryptocurrencies.
    
    Args:
        symbols: List of crypto ticker symbols (with or without -USD suffix)
    
    Returns:
        List of dictionaries with crypto quote data
    """
    results = []
    
    # Ensure all symbols have -USD suffix
    normalized_symbols = []
    for sym in symbols:
        if not sym.endswith('-USD'):
            normalized_symbols.append(f"{sym}-USD")
        else:
            normalized_symbols.append(sym)
    
    try:
        tickers = yf.Tickers(' '.join(normalized_symbols))
        for symbol in normalized_symbols:
            try:
                ticker = tickers.tickers.get(symbol.upper())
                if ticker:
                    info = ticker.info
                    if info and ('symbol' in info or 'shortName' in info):
                        results.append({
                            'symbol': info.get('symbol', symbol),
                            'name': info.get('shortName') or info.get('name'),
                            'price': info.get('regularMarketPrice'),
                            'change': info.get('regularMarketChange'),
                            'changePercent': info.get('regularMarketChangePercent'),
                            'volume': info.get('regularMarketVolume'),
                            'marketCap': info.get('marketCap'),
                            'high52w': info.get('fiftyTwoWeekHigh'),
                            'low52w': info.get('fiftyTwoWeekLow'),
                            'currency': 'USD',
                        })
            except Exception as e:
                logger.warning(f"Error fetching crypto {symbol}: {e}")
    except Exception as e:
        logger.error(f"Error fetching multiple crypto quotes: {e}")
    
    return results


def get_crypto_history(
    symbol: str, 
    period: str = '1mo', 
    interval: str = '1d'
) -> List[Dict[str, Any]]:
    """
    Get historical OHLCV data for a cryptocurrency.
    
    Args:
        symbol: Crypto ticker symbol (e.g., 'BTC-USD' or 'BTC')
        period: Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval: Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    
    Returns:
        List of OHLCV dictionaries
    """
    # Ensure symbol has -USD suffix
    if not symbol.endswith('-USD'):
        symbol = f"{symbol}-USD"
    
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
        logger.error(f"Error fetching crypto history for {symbol}: {e}")
        return []


def get_top_cryptos(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get quotes for top cryptocurrencies.
    
    Args:
        limit: Number of top cryptos to return (max 20)
    
    Returns:
        List of crypto quote dictionaries
    """
    symbols = TOP_CRYPTOS[:min(limit, len(TOP_CRYPTOS))]
    return get_multiple_crypto_quotes(symbols)


def import_cryptos_to_db(symbols: List[str] = None, db_session=None, country_code: str = 'GLOBAL') -> Dict[str, int]:
    """
    Import cryptocurrency data to database.
    
    Args:
        symbols: List of crypto ticker symbols (defaults to TOP_CRYPTOS)
        db_session: SQLAlchemy database session
        country_code: Country code to assign (default: GLOBAL since crypto is global)
    
    Returns:
        Dictionary with counts of imported and updated records
    """
    from models import db, MarketData
    
    if symbols is None:
        symbols = TOP_CRYPTOS
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    for symbol in symbols:
        try:
            quote = get_crypto_quote(symbol)
            if not quote:
                errors += 1
                continue
            
            # Normalize symbol (remove -USD for storage if needed)
            store_symbol = quote.get('symbol', symbol)
            
            # Check if exists
            existing = MarketData.query.filter_by(
                symbol=store_symbol,
                asset_type='crypto',
                country_code=country_code
            ).first()
            
            if existing:
                # Update existing record
                existing.name = quote.get('name')
                existing.price = quote.get('price')
                existing.change = quote.get('change')
                existing.change_percent = quote.get('changePercent')
                existing.volume = quote.get('volume')
                existing.market_cap = quote.get('marketCap')
                existing._52_week_high = quote.get('high52w')
                existing._52_week_low = quote.get('low52w')
                existing.previous_close = quote.get('previousClose')
                existing.open_price = quote.get('open')
                existing.day_high = quote.get('dayHigh')
                existing.day_low = quote.get('dayLow')
                existing.avg_volume = quote.get('avgVolume')
                existing.currency = 'USD'
                existing.exchange = quote.get('exchange')
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                # Create new record
                new_crypto = MarketData(
                    symbol=store_symbol,
                    name=quote.get('name'),
                    price=quote.get('price'),
                    change=quote.get('change'),
                    change_percent=quote.get('changePercent'),
                    volume=quote.get('volume'),
                    market_cap=quote.get('marketCap'),
                    _52_week_high=quote.get('high52w'),
                    _52_week_low=quote.get('low52w'),
                    previous_close=quote.get('previousClose'),
                    open_price=quote.get('open'),
                    day_high=quote.get('dayHigh'),
                    day_low=quote.get('dayLow'),
                    avg_volume=quote.get('avgVolume'),
                    currency='USD',
                    exchange=quote.get('exchange'),
                    asset_type='crypto',
                    country_code=country_code,
                    last_updated=datetime.utcnow(),
                )
                session.add(new_crypto)
                imported += 1
        except Exception as e:
            logger.error(f"Error importing crypto {symbol}: {e}")
            errors += 1
    
    try:
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Error committing cryptos to database: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(symbols)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}
