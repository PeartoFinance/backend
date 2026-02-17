"""
Stock Data Handler - YFinance Integration
Functions for fetching stock data from Yahoo Finance
"""
import yfinance as yf
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
from . import get_yfinance_session

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
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        info = ticker.info
        quote_type = info.get('quoteType') # Returns 'ETF' or 'EQUITY'
        asset_type = 'etf' if quote_type == 'ETF' else 'stock'
        
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
            'quoteType': info.get('quoteType'),
        }
    except Exception as e:
        logger.error(f"Error fetching quote for {symbol}: {e}")
        return None


def get_multiple_quotes(symbols: List[str]) -> List[Dict[str, Any]]:
    """
    Get real-time quotes for multiple stock symbols.
    
    [PERFORMANCE FIX] Uses yf.download for batch price fetching (1 request) 
    and DB lookup for static metadata to avoid IP bans and improve speed.
    
    Args:
        symbols: List of stock ticker symbols
    
    Returns:
        List of dictionaries with stock quote data
    """
    from .rate_limiter import check_rate_limit, report_yfinance_error, report_yfinance_success
    from models import MarketData
    import pandas as pd
    import numpy as np
    
    results = []
    if not symbols:
        return results
        
    # Check rate limit before making request
    if not check_rate_limit():
        logger.warning("[Stock Handler] Rate limited, returning empty list")
        return results
    
    try:
        # 1. Bulk Fetch prices (One API call for up to 50+ tickers)
        yf_session = get_yfinance_session()
        # threads=False is used for shared hosting compatibility
        tickers_data = yf.download(
            symbols, 
            period='1d', 
            interval='1m', 
            group_by='ticker', 
            threads=False, 
            progress=False, 
            session=yf_session
        )
        
        # 2. Fetch static metadata (names, sectors) from DB in one query to avoid 50 individual .info calls
        db_stocks = MarketData.query.filter(MarketData.symbol.in_(symbols)).all()
        db_map = {s.symbol.upper(): s for s in db_stocks}
        
        for symbol in symbols:
            symbol = symbol.upper()
            try:
                # Extract this specific ticker from the bulk response
                if len(symbols) > 1:
                    # In group_by='ticker' mode, columns are MultiIndex: (Symbol, Field)
                    if symbol in tickers_data.columns.levels[0]:
                        ticker_df = tickers_data[symbol]
                    else:
                        ticker_df = None
                else:
                    ticker_df = tickers_data
                
                # Fetch cached/static metadata from our database
                stock_md = db_map.get(symbol)
                
                if ticker_df is not None and not ticker_df.empty and 'Close' in ticker_df.columns:
                    # Successfully got live price from true batch fetch
                    latest_row = ticker_df.iloc[-1]
                    first_row = ticker_df.iloc[0]
                    
                    def sanitize(val, default=0.0):
                        return float(val) if not pd.isna(val) else default

                    price = sanitize(latest_row['Close'])
                    # Estimate change since open of the interval
                    open_price = sanitize(first_row['Open'])
                    change = price - open_price
                    change_pct = (change / open_price * 100) if open_price != 0 else 0
                    
                    # Merge Batch Price with localized metadata
                    results.append({
                        'symbol': symbol,
                        'name': stock_md.name if stock_md else symbol,
                        'price': price,
                        'change': change,
                        'changePercent': change_pct,
                        'volume': int(latest_row['Volume']) if 'Volume' in ticker_df.columns and not pd.isna(latest_row['Volume']) else 0,
                        'marketCap': stock_md.market_cap if stock_md else None,
                        'peRatio': float(stock_md.pe_ratio) if stock_md and stock_md.pe_ratio else None,
                        'high52w': float(stock_md._52_week_high) if stock_md and stock_md._52_week_high else None,
                        'low52w': float(stock_md._52_week_low) if stock_md and stock_md._52_week_low else None,
                        'sector': stock_md.sector if stock_md else None,
                        'industry': stock_md.industry if stock_md else None,
                        'exchange': stock_md.exchange if stock_md else None,
                        'currency': stock_md.currency if stock_md else 'USD',
                        'quoteType': stock_md.asset_type.upper() if stock_md and stock_md.asset_type else 'EQUITY',
                    })
                else:
                    # Fallback to individual .info call ONLY for stickers missing from batch or DB
                    # This ensures reliability for new or obscure symbols
                    single = get_stock_quote(symbol)
                    if single:
                        results.append(single)
            except Exception as e:
                logger.warning(f"Error processing {symbol} in batch: {e}")

        if results:
            report_yfinance_success()
            logger.info(f"[Stock Handler] Fetched {len(results)}/{len(symbols)} quotes (True Batch)")
            
    except Exception as e:
        # Check for rate limit error in bulk request
        error_msg = str(e)
        is_rate_limit = 'Too Many Requests' in error_msg or '429' in error_msg
        report_yfinance_error(is_rate_limit=is_rate_limit)
        logger.error(f"Batch quote fetch failed: {e}")
    
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
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return []
        
        results = []
        for date, row in hist.iterrows():
            # Use isoformat to include time for intraday data (1m, 5m, 1h, etc.)
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
        logger.error(f"Error fetching history for {symbol}: {e}")
        return []


def save_stock_history_to_db(symbol: str, history_data: List[Dict[str, Any]], interval: str = '1d'):
    """
    Save historical OHLCV data to the database.
    """
    from models import db, StockPriceHistory
    from datetime import datetime
    
    symbol = symbol.upper()
    count = 0
    
    for entry in history_data:
        try:
            # Parse date - handle both date strings and ISO timestamps
            date_str = entry['date']
            if 'T' in date_str:
                dt = datetime.fromisoformat(date_str)
            else:
                dt = datetime.strptime(date_str, '%Y-%m-%d')
            
            # Check if record already exists
            existing = StockPriceHistory.query.filter_by(
                symbol=symbol,
                date=dt.date(),
                interval=interval
            ).first()
            
            if not existing:
                new_history = StockPriceHistory(
                    symbol=symbol,
                    date=dt.date(),
                    open_price=entry.get('open'),
                    high=entry.get('high'),
                    low=entry.get('low'),
                    close=entry.get('close'),
                    volume=entry.get('volume'),
                    interval=interval
                )
                db.session.add(new_history)
                count += 1
        except Exception as e:
            logger.error(f"Error saving history record for {symbol} on {entry.get('date')}: {e}")
            continue
            
    try:
        db.session.commit()
        return count
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error committing history to DB for {symbol}: {e}")
        return 0


def get_recommendations(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get analyst recommendations for a stock.
    
    Returns:
        Dictionary with recommendation summary and recent upgrades/downgrades
    """
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        
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
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
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


def import_stocks_to_db(symbols: List[str], db_session=None, country_code: str = 'GLOBAL') -> Dict[str, int]:
    """
    Import stock data to database using bulk fetching to prevent IP bans.
    """
    from models import db, MarketData
    
    session = db_session or db.session
    imported = 0
    updated = 0
    errors = 0
    
    try:
        # Bulk fetch all prices in one request (much faster and safer for production)
        yf_session = get_yfinance_session()
        tickers_data = yf.download(symbols, period='1d', interval='1m', group_by='ticker', threads=False, progress=False, session=yf_session)
        
        if tickers_data is None or (hasattr(tickers_data, 'empty') and tickers_data.empty):
            logger.warning(f"Bulk download returned no data for symbols: {symbols}")
            return {'imported': 0, 'updated': 0, 'errors': len(symbols)}

        for symbol in symbols:
            try:
                symbol = symbol.upper()
                
                # Get data for this specific ticker from the bulk result
                if len(symbols) > 1:
                    ticker_df = tickers_data[symbol]
                else:
                    ticker_df = tickers_data
                    
                if ticker_df.empty:
                    # Fallback to single quote if bulk failed for this symbol
                    quote = get_stock_quote(symbol)
                elif 'Close' not in ticker_df.columns or 'Open' not in ticker_df.columns:
                    # Missing required columns, fallback to single quote
                    logger.warning(f"Missing price data for {symbol} in bulk download")
                    quote = get_stock_quote(symbol)
                else:
                    # Extract basic info from bulk data
                    import pandas as pd
                    import numpy as np
                    
                    def sanitize_float(val, default=0.0):
                        try:
                            if pd.isna(val) or np.isnan(val):
                                return default
                            return float(val)
                        except:
                            return default
                    
                    latest_price = sanitize_float(ticker_df['Close'].iloc[-1])
                    prev_close = sanitize_float(ticker_df['Open'].iloc[0])
                    change = latest_price - prev_close
                    change_pct = (change / prev_close * 100) if prev_close != 0 else 0
                    
                    # Handle volume safely
                    if 'Volume' in ticker_df.columns:
                        vol_val = ticker_df['Volume'].iloc[-1]
                        volume = 0 if pd.isna(vol_val) else int(vol_val)
                    else:
                        volume = 0

                    quote = {
                        'symbol': symbol,
                        'price': latest_price,
                        'change': sanitize_float(change),
                        'changePercent': sanitize_float(change_pct),
                        'volume': volume,
                        'open': sanitize_float(ticker_df['Open'].iloc[-1]),
                        'dayHigh': sanitize_float(ticker_df['High'].max()),
                        'dayLow': sanitize_float(ticker_df['Low'].min()),
                    }


                if not quote or not quote.get('price'):
                    errors += 1
                    continue
                
                # Check if exists
                existing = MarketData.query.filter_by(
                    symbol=symbol,
                    country_code=country_code
                ).first()
                
                if existing:
                    # Update price and basic metrics
                    existing.price = quote.get('price')
                    existing.change = quote.get('change')
                    existing.change_percent = quote.get('changePercent')
                    existing.volume = quote.get('volume')
                    existing.open_price = quote.get('open')
                    existing.day_high = quote.get('dayHigh')
                    existing.day_low = quote.get('dayLow')
                    existing.last_updated = datetime.utcnow()
                    updated += 1
                else:
                    # For new stocks, we still need full info once
                    full_quote = get_stock_quote(symbol)
                    if full_quote:
                        new_stock = MarketData(
                            symbol=symbol,
                            name=full_quote.get('name', symbol),
                            price=full_quote.get('price', 0),
                            change=full_quote.get('change', 0),
                            change_percent=full_quote.get('changePercent', 0),
                            asset_type='etf' if full_quote.get('quoteType') == 'ETF' else 'stock',
                            country_code=country_code,
                            is_listed=True,
                            currency=full_quote.get('currency', 'USD'),
                            last_updated=datetime.utcnow()
                        )
                        session.add(new_stock)
                        imported += 1
            except Exception as e:
                logger.error(f"Error processing {symbol} in bulk: {e}")
                errors += 1
                
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Bulk import failed: {e}")
        return {'imported': 0, 'updated': 0, 'errors': len(symbols)}
    
    return {'imported': imported, 'updated': updated, 'errors': errors}


def _detect_stock_news_category(title, summary=''):
    """Auto-detect news category using shared keyword detection."""
    try:
        from services.news_source_manager import detect_category
        return detect_category(title, summary)
    except ImportError:
        return 'business'  # Fallback for stock-related news


def sync_stock_news(symbol: str) -> Dict[str, Any]:
    """
    Fetch news for a specific stock from yfinance and save to database.
    """
    from models import db, NewsItem
    import hashlib
    import re
    
    symbol = symbol.upper()
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        news = ticker.news
        
        if not news:
            return {'status': 'ok', 'added': 0, 'message': f'No news found for {symbol}'}
            
        added_count = 0
        for item in news:
            # Extract content (yfinance news structure can vary slightly)
            content = item.get('content', item)
            title = content.get('title')
            link = content.get('canonicalUrl', {}).get('url') or content.get('link')
            
            if not title or not link:
                continue
                
            # Generate a unique hash for deduplication
            item_hash = hashlib.sha256(f"{link}|{title}".encode('utf-8')).hexdigest()
            
            # Check if already exists
            existing = NewsItem.query.filter_by(hash=item_hash).first()
            if existing:
                continue
                
            # Generate slug
            slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:100]
            # Ensure slug uniqueness (simplified)
            if NewsItem.query.filter_by(slug=slug).first():
                slug = f"{slug}-{int(datetime.utcnow().timestamp())}"

            # Parse date
            pub_date = None
            pub_date_str = content.get('pubDate') or content.get('pubtime')
            if pub_date_str:
                try:
                    pub_date = datetime.fromisoformat(pub_date_str.replace('Z', '+00:00'))
                except:
                    pub_date = datetime.utcnow()
            else:
                pub_date = datetime.utcnow()

            # Get image
            image_url = None
            thumbnail = content.get('thumbnail', {})
            if thumbnail:
                resolutions = thumbnail.get('resolutions', [])
                if resolutions:
                    # Pick the highest resolution
                    image_url = resolutions[-1].get('url')

            new_news = NewsItem(
                title=title,
                summary=content.get('summary') or title,
                canonical_url=link,
                source=content.get('provider', {}).get('displayName') or 'Yahoo Finance',
                published_at=pub_date,
                hash=item_hash,
                slug=slug,
                related_symbol=symbol,
                curated_status='published', # Auto-publish stock-specific news
                source_type='yfinance',
                image=image_url,
                category=_detect_stock_news_category(title, content.get('summary') or ''),
                created_at=datetime.utcnow()
            )
            db.session.add(new_news)
            added_count += 1

            
        db.session.commit()
        return {'status': 'success', 'added': added_count, 'message': f'Added {added_count} news items for {symbol}'}
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing news for {symbol}: {e}")
        return {'status': 'error', 'message': str(e)}


def fetch_stock_news_preview(symbol: str) -> Dict[str, Any]:
    """
    Fetch news for a specific stock from yfinance and return as list (without saving).
    """
    import hashlib
    import re
    
    symbol = symbol.upper()
    try:
        session = get_yfinance_session()
        ticker = yf.Ticker(symbol, session=session)
        news = ticker.news
        
        if not news:
            return {'status': 'ok', 'items': [], 'message': f'No news found for {symbol}'}
        
        preview_items = []
        for item in news:
            # Extract content
            content = item.get('content', item)
            title = content.get('title')
            link = content.get('canonicalUrl', {}).get('url') or content.get('link')
            
            if not title or not link:
                continue
                
            # Parse date
            pub_date = None
            pub_date_str = content.get('pubDate') or content.get('pubtime')
            if pub_date_str:
                try:
                    # Keep as string for JSON serialization
                    pub_date = pub_date_str
                except:
                    pub_date = datetime.utcnow().isoformat()
            else:
                pub_date = datetime.utcnow().isoformat()

            # Get image
            image_url = None
            thumbnail = content.get('thumbnail', {})
            if thumbnail:
                resolutions = thumbnail.get('resolutions', [])
                if resolutions:
                    image_url = resolutions[-1].get('url')

            preview_items.append({
                'title': title,
                'summary': content.get('summary') or title,
                'canonical_url': link,
                'source': content.get('provider', {}).get('displayName') or 'Yahoo Finance',
                'published_at': pub_date,
                'related_symbol': symbol,
                'image': image_url,
                'source_type': 'yfinance'
            })
            
        return {'status': 'success', 'items': preview_items}
        
    except Exception as e:
        logger.error(f"Error fetching news preview for {symbol}: {e}")
        return {'status': 'error', 'message': str(e)}
