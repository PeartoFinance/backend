"""
Live Data API Routes
Real-time quotes and intraday data for live chart updates

Optimized for rate limiting with:
- Aggressive caching (5 min default)
- Database fallback when yfinance fails
- Smart request throttling
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from extensions import cache, limiter
from handlers.market_data.screener_handler import get_day_gainers, get_day_losers, get_most_active
from handlers.market_data.rate_limiter import check_rate_limit, report_yfinance_error, report_yfinance_success
from models.market import MarketData
from utils.validators import safe_int, safe_float
from utils.market_hours import get_market_status_summary
import time
import logging

logger = logging.getLogger(__name__)

live_bp = Blueprint('live', __name__)

# Cache timeout in seconds (5 minutes for most routes)
CACHE_TIMEOUT_DEFAULT = 300  # 5 minutes
CACHE_TIMEOUT_DASHBOARD = 300  # 5 minutes
CACHE_TIMEOUT_LIVE = 60  # 1 minute for truly "live" endpoints
CACHE_TIMEOUT_MOVERS = 180  # 3 minutes for movers

# Helper for unified market data formatting
def _format_market_item(item, asset_type='stock'):
    """Unifies market data formatting for live routes"""
    if not item: return None
    
    # Use 'if key in item' to avoid treating 0 as falsy
    price = item.get('price') if item.get('price') is not None else (item.get('currentPrice') if item.get('currentPrice') is not None else item.get('regularMarketPrice'))
    change = item.get('change') if item.get('change') is not None else item.get('regularMarketChange')
    change_p = item.get('changePercent') if item.get('changePercent') is not None else item.get('regularMarketChangePercent')
    
    # Sanitize: if price is 0 or None, don't report bogus change values
    if price is not None and float(price) == 0:
        price = None
    if price is None:
        change = None
        change_p = None
    
    # Infer asset type if missing
    calculated_asset_type = item.get('assetType') or asset_type
    if not item.get('assetType'):
        if item.get('quoteType') == 'CRYPTOCURRENCY' or item.get('sector') == 'Cryptocurrency':
            calculated_asset_type = 'crypto'
        elif item.get('quoteType') in ['ETF', 'EQUITY']:
            calculated_asset_type = 'stock'

    return {
        'symbol': item.get('symbol'),
        'name': item.get('shortName') or item.get('name') or item.get('displayName'),
        'price': float(price) if price is not None else None,
        'change': float(change) if change is not None else None,
        'changePercent': float(change_p) if change_p is not None else None,
        'volume': item.get('volume') or item.get('regularMarketVolume'),
        'marketCap': item.get('marketCap'),
        'assetType': calculated_asset_type,
        'currency': item.get('currency', 'USD'),
        'exchange': item.get('exchange'),
        'lastUpdated': datetime.utcnow().isoformat()
    }


@live_bp.route('/quote/<symbol>', methods=['GET'])
@limiter.limit("60 per minute")
def get_live_quote(symbol):
    """Get real-time quote for a single symbol using direct handlers"""
    symbol = symbol.upper()
    
    # Try stock handler first (covers most including ETFs)
    from handlers.market_data.stock_handler import get_stock_quote, get_multiple_quotes
    from handlers.market_data.crypto_handler import get_crypto_quote
    from models.market import MarketData

    # Simple heuristic: if it contains '-', likely crypto (e.g., BTC-USD)
    
    # Simple heuristic: if it contains '-', likely crypto (e.g., BTC-USD)
    data = None
    if '-' in symbol:
        data = get_crypto_quote(symbol)
    
    if not data:
        data = get_stock_quote(symbol)
        
    if not data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    return jsonify(_format_market_item(data))


@live_bp.route('/quotes', methods=['GET'])
@limiter.limit("30 per minute")
def get_live_quotes():
    """Get real-time quotes for multiple symbols using direct handlers"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
    
    if len(symbols) > 20: # increased limit for batch support
        return jsonify({'error': 'Maximum 20 symbols allowed'}), 400
        
    # Use stock handler's batch fetch which handles generic tickers
    from handlers.market_data.stock_handler import get_multiple_quotes
    
    results = get_multiple_quotes(symbols)
    return jsonify([_format_market_item(r) for r in results if r])


@live_bp.route('/intraday/<symbol>', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_LIVE, query_string=True)
@limiter.limit("20 per minute")
def get_live_intraday(symbol):
    """
    Get recent intraday data for live charts.
    Directly fetches from yfinance via handlers.
    """
    from handlers.market_data.stock_handler import get_stock_history
    
    symbol = symbol.upper()
    try:
        # Get last 1 day of 5-minute data (better for intraday view)
        # Using 5m interval for reliability, or 1m if needed. 
        # User wants "live", 1m is best.
        history = get_stock_history(symbol, period='1d', interval='1m')
        
        if not history:
            return jsonify({'error': 'No intraday data available'}), 404
            
        return jsonify({
            'symbol': symbol,
            'interval': '1m',
            'data': history
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@live_bp.route('/market-pulse', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_MOVERS, query_string=True)
@limiter.limit("10 per minute")
def get_market_pulse():
    """
    Get quick market overview for live dashboard via direct handlers.
    Returns major indices and top movers.
    """
    try:
        # Fetch directly from external source via handlers
        # Using limit=5 as per UI requirement
        gainers = get_day_gainers(limit=5)
        losers = get_day_losers(limit=5)
        active = get_most_active(limit=5)
        
        return jsonify({
            'gainers': [_format_market_item(g) for g in gainers],
            'losers': [_format_market_item(l) for l in losers],
            'mostActive': [_format_market_item(a) for a in active],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        logger.error(f"Market pulse error: {e}")
        return jsonify({'error': 'Failed to fetch market pulse'}), 500


@live_bp.route('/search', methods=['GET'])
@limiter.limit("30 per minute")
def search_live_symbols():
    """
    Search symbols with live prices via direct handler.
    Supports stocks, crypto, indices, and commodities.
    """
    from handlers.market_data.search_handler import search_tickers
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
        
    try:
        # Use direct search handler
        # Max 10 results adequate for dropdown
        results = search_tickers(query, max_results=10)
        
        quotes = results.get('quotes', [])
        
        # Format for frontend
        formatted = []
        for q in quotes:
            formatted.append({
                'symbol': q.get('symbol'),
                'name': q.get('name'),
                'type': q.get('typeDisplay') or q.get('type'),
                'exchange': q.get('exchangeDisplay') or q.get('exchange'),
                'price': None, # Search handler might not return price, frontend should fetch if needed or just show symbol
                'assetType': 'stock' if q.get('type') == 'EQUITY' else 'crypto' if q.get('type') == 'CRYPTOCURRENCY' else 'other'
            })
            
        return jsonify(formatted)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@live_bp.route('/dashboard', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DASHBOARD, query_string=True)
@limiter.limit("10 per minute")
def get_live_dashboard():
    """
    Get comprehensive live dashboard data via direct handlers.
    Returns indices, commodities, top movers, and market pulse.
    """
    from handlers.market_data.index_handler import get_all_major_indices
    from handlers.market_data.commodity_handler import get_all_commodities
    from handlers.market_data.screener_handler import get_day_gainers, get_day_losers, get_most_active
    from handlers.market_data.crypto_handler import get_multiple_crypto_quotes, TOP_CRYPTOS
    
    try:
        # 1. Market Indices (major ones)
        indices = get_all_major_indices() or []
        
        # 2. Commodities
        commodities = get_all_commodities() or []
        
        # 3. Top Stocks (Gainers/Losers/Active)
        gainers = get_day_gainers(limit=5) or []
        losers = get_day_losers(limit=5) or []
        active = get_most_active(limit=5) or []
        
        # 4. Top Crypto
        # Use top 6 from defined list
        crypto = get_multiple_crypto_quotes(TOP_CRYPTOS[:6]) or []
        
        # Format helpers
        def format_index(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('displayName') or item.get('name'), # index handler adds displayName
                'price': _price,
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'assetType': 'index'
            }

        def format_comm(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': _price,
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'assetType': 'commodity',
                'unit': item.get('unit')
            }
            
        def format_stock(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            vol = item.get('volume')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': _price,
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'assetType': 'stock',
                'volume': vol
            }
            
        def format_crypto(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': _price,
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'assetType': 'crypto'
            }

        # Taking top 8 indices and 6 commodities as per old limit
        return jsonify({
            'indices': [format_index(i) for i in indices[:8]],
            'commodities': [format_comm(c) for c in commodities[:6]],
            'gainers': [format_stock(g) for g in gainers],
            'losers': [format_stock(l) for l in losers],
            'mostActive': [format_stock(a) for a in active],
            'crypto': [format_crypto(c) for c in crypto],
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Live dashboard error: {e}")
        return jsonify({'error': 'Failed to fetch dashboard data'}), 500


@live_bp.route('/overview', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DASHBOARD, query_string=True)
def get_live_overview():
    """
    Get comprehensive live market overview.
    Aggregates indices, top movers, and active stocks.
    """
    from handlers.market_data.index_handler import get_all_major_indices
    from handlers.market_data.screener_handler import get_day_gainers, get_day_losers, get_most_active
    
    try:
        # 1. Market Indices
        indices = get_all_major_indices() or []
        
        # 2. Top Stocks (Gainers/Losers/Active)
        gainers = get_day_gainers(limit=5) or []
        losers = get_day_losers(limit=5) or []
        most_active = get_most_active(limit=5) or []
        
        # Helpers
        def format_index(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('displayName') or item.get('name'),
                'value': _price, # Frontend expects 'value' for indices
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'marketStatus': get_market_status_summary().get('label', 'REGULAR'),
                'lastUpdated': datetime.utcnow().isoformat()
            }
            
        def format_stock(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            vol = item.get('volume')
            _price = float(price) if price is not None and float(price) > 0 else None
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': _price,
                'change': float(change) if (_price is not None and change is not None) else None,
                'changePercent': float(change_p) if (_price is not None and change_p is not None) else None,
                'volume': int(vol) if vol else None,
                'assetType': 'stock'
            }

        # Compute breadth from available data
        all_stocks = gainers + losers + most_active
        # Deduplicate by symbol
        seen = set()
        unique_stocks = []
        for s in all_stocks:
            sym = s.get('symbol')
            if sym and sym not in seen:
                seen.add(sym)
                unique_stocks.append(s)
        
        adv = sum(1 for s in unique_stocks if (s.get('changePercent') or s.get('change') or 0) > 0)
        dec = sum(1 for s in unique_stocks if (s.get('changePercent') or s.get('change') or 0) < 0)
        unch = len(unique_stocks) - adv - dec

        return jsonify({
            'indices': [format_index(i) for i in indices[:6]],
            'topGainers': [format_stock(g) for g in gainers],
            'topLosers': [format_stock(l) for l in losers],
            'mostActive': [format_stock(a) for a in most_active],
            'advancers': adv,
            'decliners': dec,
            'unchanged': unch,
            'totalVolume': sum(s.get('volume', 0) for s in most_active) * 10, # Rough estimate
            'marketStatus': get_market_status_summary(),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@live_bp.route('/stocks', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_live_stocks():
    """
    Get live data for a list of stocks with pagination.
    """
    from handlers.market_data.stock_handler import get_multiple_quotes
    from models.market import MarketData
    from utils.validators import safe_pagination
    
    sector = request.args.get('sector')
    limit, offset = safe_pagination(
        request.args.get('limit'),
        request.args.get('offset'),
        max_limit=100,
        max_offset=10000
    )
    # Calculate page from offset for backward compatibility
    page = (offset // limit) + 1
    
    header_country = request.headers.get('X-User-Country')
    # Use DB to get relevant symbols
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        md_filter = (MarketData.country_code == 'GLOBAL')
        
    query = MarketData.query.with_entities(MarketData.symbol).filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        md_filter
    )
    
    if sector:
        query = query.filter(MarketData.sector == sector)
        
    # Order by market cap to show most relevant
    symbols = [s[0] for s in query.offset(offset).limit(limit).all()]
    
    if not symbols:
        return jsonify([])
        
    # fetch full objects to check freshness
    from models.market import MarketData as MarketDataModel
    db_stocks = MarketDataModel.query.filter(
        MarketDataModel.symbol.in_(symbols)
    ).all()
    
    # Check if DB data is fresh (within 15 minutes) AND has valid prices
    fresh_cutoff = datetime.utcnow() - timedelta(minutes=15)
    all_fresh = all(
        s.last_updated and s.last_updated > fresh_cutoff and s.price and float(s.price) > 0
        for s in db_stocks
    ) if db_stocks else False
    
    quotes = []
    if all_fresh and db_stocks:
        # Use DB data directly
        for stock in db_stocks:
            _price = float(stock.price) if stock.price is not None and float(stock.price) > 0 else None
            quotes.append({
                'symbol': stock.symbol,
                'name': stock.name,
                'price': _price,
                'change': float(stock.change) if (_price is not None and stock.change is not None) else None,
                'changePercent': float(stock.change_percent) if (_price is not None and stock.change_percent is not None) else None,
                'volume': stock.volume,
                'marketCap': stock.market_cap,
                'peRatio': float(stock.pe_ratio) if stock.pe_ratio else None,
                'high52w': float(stock._52_week_high) if stock._52_week_high else None,
                'low52w': float(stock._52_week_low) if stock._52_week_low else None,
                'sector': stock.sector,
                'industry': stock.industry,
                'exchange': stock.exchange,
                'currency': stock.currency,
                'quoteType': 'EQUITY' if stock.asset_type == 'stock' else 'ETF',
                'assetType': stock.asset_type
            })
    else:
        # Fetch live if any are stale or it's a fresh restart
        from handlers.market_data.stock_handler import get_multiple_quotes
        quotes = get_multiple_quotes(symbols)
        
        # Fallback to DB if live fetch failed
        if not quotes or len(quotes) < len(symbols) * 0.5:
            # Re-map using what we already fetched from DB
            live_map = {q['symbol']: q for q in quotes}
            quotes = []
            for stock in db_stocks:
                if stock.symbol in live_map:
                    quotes.append(live_map[stock.symbol])
                else:
                    _price = float(stock.price) if stock.price is not None and float(stock.price) > 0 else None
                    quotes.append({
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'price': _price,
                        'change': float(stock.change) if (_price is not None and stock.change is not None) else None,
                        'changePercent': float(stock.change_percent) if (_price is not None and stock.change_percent is not None) else None,
                        'volume': stock.volume,
                        'marketCap': stock.market_cap,
                        'peRatio': float(stock.pe_ratio) if stock.pe_ratio else None,
                        'high52w': float(stock._52_week_high) if stock._52_week_high else None,
                        'low52w': float(stock._52_week_low) if stock._52_week_low else None,
                        'sector': stock.sector,
                        'industry': stock.industry,
                        'exchange': stock.exchange,
                        'currency': stock.currency,
                        'quoteType': 'EQUITY' if stock.asset_type == 'stock' else 'ETF',
                        'assetType': stock.asset_type
                    })

    return jsonify([_format_market_item(q, 'stock') for q in quotes if q])


@live_bp.route('/crypto', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_live_crypto():
    """Get live crypto data with pagination"""
    from handlers.market_data.crypto_handler import get_multiple_crypto_quotes, TOP_CRYPTOS
    from models.market import MarketData
    from utils.validators import safe_pagination
    
    limit, offset = safe_pagination(
        request.args.get('limit'),
        request.args.get('offset'),
        max_limit=50,
        max_offset=5000
    )
    # Calculate page from offset for backward compatibility
    page = (offset // limit) + 1
    
    # Prioritize DB symbols if we rely on user-added ones, else use top list + DB
    # For now, let's use the TOP_CRYPTOS constant + some major ones from DB
    
    db_symbols = [s[0] for s in MarketData.query.with_entities(MarketData.symbol).filter(
        MarketData.asset_type == 'crypto'
    ).offset(offset).limit(limit).all()]
    
    # Merge unique
    all_symbols = list(set(TOP_CRYPTOS + db_symbols))[:limit]
    
    # Fetch from DB first to check for freshness
    db_crypto = MarketData.query.filter(
        MarketData.asset_type == 'crypto',
        MarketData.symbol.in_(all_symbols)
    ).all()
    
    fresh_cutoff = datetime.utcnow() - timedelta(minutes=15)
    all_fresh = all(c.last_updated and c.last_updated > fresh_cutoff and c.price and float(c.price) > 0 for c in db_crypto) if db_crypto else False
    
    quotes = []
    if all_fresh and db_crypto:
        for c in db_crypto:
            _price = float(c.price) if c.price is not None and float(c.price) > 0 else None
            quotes.append({
                'symbol': c.symbol,
                'name': c.name,
                'price': _price,
                'change': float(c.change) if (_price is not None and c.change is not None) else None,
                'changePercent': float(c.change_percent) if (_price is not None and c.change_percent is not None) else None,
                'volume': c.volume,
                'marketCap': c.market_cap,
                'currency': c.currency,
                'quoteType': 'CRYPTOCURRENCY',
                'assetType': 'crypto'
            })
    else:
        # Either stale or forced refresh needed
        from handlers.market_data.crypto_handler import get_multiple_crypto_quotes
        quotes = get_multiple_crypto_quotes(all_symbols)
        
        # Fallback to DB if live fetch failed
        if not quotes:
            for c in db_crypto:
                _price = float(c.price) if c.price is not None and float(c.price) > 0 else None
                quotes.append({
                    'symbol': c.symbol,
                    'name': c.name,
                    'price': _price,
                    'change': float(c.change) if (_price is not None and c.change is not None) else None,
                    'changePercent': float(c.change_percent) if (_price is not None and c.change_percent is not None) else None,
                    'volume': c.volume,
                    'marketCap': c.market_cap,
                    'currency': c.currency,
                    'quoteType': 'CRYPTOCURRENCY',
                    'assetType': 'crypto'
                })
            
    return jsonify([_format_market_item(q, 'crypto') for q in quotes if q])


@live_bp.route('/commodities', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_live_commodities():
    from handlers.market_data.commodity_handler import get_all_commodities
    from models.market import CommodityData
    
    # Check DB first
    db_commodities = CommodityData.query.all()
    fresh_cutoff = datetime.utcnow() - timedelta(minutes=15)
    all_fresh = all(c.last_updated and c.last_updated > fresh_cutoff and c.price and float(c.price) > 0 for c in db_commodities) if db_commodities else False
    
    commodities = []
    if all_fresh and db_commodities:
        for c in db_commodities:
            _price = float(c.price) if c.price is not None and float(c.price) > 0 else None
            commodities.append({
                'symbol': c.symbol,
                'name': c.name,
                'price': _price,
                'change': float(c.change) if (_price is not None and c.change is not None) else None,
                'changePercent': float(c.change_percent) if (_price is not None and c.change_percent is not None) else None,
                'dayHigh': float(c.day_high) if c.day_high else None,
                'dayLow': float(c.day_low) if c.day_low else None,
                'unit': c.unit,
                'currency': c.currency,
                'countryCode': c.country_code
            })
    else:
        # Try live fetch
        commodities = get_all_commodities() or []
        
        if not commodities and db_commodities:
            # Fallback
            for c in db_commodities:
                _price = float(c.price) if c.price is not None and float(c.price) > 0 else None
                commodities.append({
                    'symbol': c.symbol,
                    'name': c.name,
                    'price': _price,
                    'change': float(c.change) if (_price is not None and c.change is not None) else None,
                    'changePercent': float(c.change_percent) if (_price is not None and c.change_percent is not None) else None,
                    'dayHigh': float(c.day_high) if c.day_high else None,
                    'dayLow': float(c.day_low) if c.day_low else None,
                    'unit': c.unit,
                    'currency': c.currency,
                    'countryCode': c.country_code
                })
            
    return jsonify(commodities)


@live_bp.route('/forex', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_live_forex():
    """Get live forex rates with DB fallback"""
    from handlers.market_data.forex_handler import COMMON_CURRENCIES, get_forex_quote
    from models.market import MarketData
    
    # Fetch all common currencies live
    results = []
    
    for currency, symbol in COMMON_CURRENCIES.items():
        try:
            quote = get_forex_quote(symbol)
            if quote:
                # Format to match expected ForexRate interface
                results.append({
                    'pair': f"USD/{currency}",
                    'rate': quote['price'],
                    'change': quote['change'],
                    'changePercent': quote['changePercent'],
                    'high': quote['high'],
                    'low': quote['low'],
                    'baseCurrency': 'USD',
                    'targetCurrency': currency
                })
        except:
            continue
            
    # Fallback to DB if live fetch returned nothing or very few
    if not results or len(results) < len(COMMON_CURRENCIES) * 0.5:
        try:
            # Forex pairs are stored in MarketData with asset_type='forex'
            # Symbols in DB might be 'EUR=X' etc. matching COMMON_CURRENCIES values
            target_symbols = list(COMMON_CURRENCIES.values())
            db_forex = MarketData.query.filter(
                MarketData.asset_type == 'forex',
                MarketData.symbol.in_(target_symbols)
            ).all()
            
            # Map DB results to fill gaps
            existing_pairs = {r['pair'] for r in results}
            
            # Reverse map symbol to currency code for constructing pair name
            symbol_to_currency = {v: k for k, v in COMMON_CURRENCIES.items()}
            
            for f in db_forex:
                currency_code = symbol_to_currency.get(f.symbol)
                if not currency_code:
                    continue
                    
                pair_name = f"USD/{currency_code}"
                if pair_name not in existing_pairs:
                    results.append({
                        'pair': pair_name,
                        'rate': float(f.price) if f.price else None,
                        'change': float(f.change) if f.change else None,
                        'changePercent': float(f.change_percent) if f.change_percent else None,
                        'high': float(f.day_high) if f.day_high else None,
                        'low': float(f.day_low) if f.day_low else None,
                        'baseCurrency': 'USD',
                        'targetCurrency': currency_code
                    })
        except Exception as e:
            print(f"DB Fallback for forex failed: {e}")
            
    return jsonify([_format_market_item(r, 'forex') for r in results if r])


@live_bp.route('/indices', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_live_indices():
    """Get live market indices with DB fallback"""
    from handlers.market_data.index_handler import get_all_major_indices
    from models.market import MarketIndices
    
    # Check DB first
    db_indices = MarketIndices.query.all()
    fresh_cutoff = datetime.utcnow() - timedelta(minutes=15)
    all_fresh = all(idx.last_updated and idx.last_updated > fresh_cutoff for idx in db_indices) if db_indices else False
    
    indices = []
    if all_fresh and db_indices:
        for idx in db_indices:
            indices.append({
                'symbol': idx.symbol,
                'name': idx.name,
                'price': idx.price,
                'change': idx.change_amount,
                'changePercent': idx.change_percent,
                'previousClose': idx.previous_close,
                'dayHigh': idx.day_high,
                'dayLow': idx.day_low,
                'yearHigh': idx.year_high,
                'yearLow': idx.year_low,
                'displayName': idx.name
            })
    else:
        # Try live fetch first
        indices = get_all_major_indices() or []
        
        if not indices and db_indices:
            # Fallback
            for idx in db_indices:
                indices.append({
                    'symbol': idx.symbol,
                    'name': idx.name,
                    'price': idx.price,
                    'change': idx.change_amount,
                    'changePercent': idx.change_percent,
                    'previousClose': idx.previous_close,
                    'dayHigh': idx.day_high,
                    'dayLow': idx.day_low,
                    'yearHigh': idx.year_high,
                    'yearLow': idx.year_low,
                    'displayName': idx.name
                })

    # Format for frontend
    formatted = []
    for item in indices:
        price = item.get('price')
        change = item.get('change')
        change_p = item.get('changePercent')
        formatted.append({
            'symbol': item.get('symbol'),
            'name': item.get('displayName') or item.get('name'),
            'value': float(price) if price else None,
            'change': float(change) if change is not None else None,
            'changePercent': float(change_p) if change_p is not None else None,
            'marketStatus': get_market_status_summary().get('label', 'REGULAR'),
            'lastUpdated': datetime.utcnow().isoformat(),
            'assetType': 'index'
        })
        
    return jsonify(formatted)


@live_bp.route('/movers', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_MOVERS, query_string=True)
def get_live_movers():
    """Get top gainers and losers live"""
    from handlers.market_data.screener_handler import get_day_gainers, get_day_losers
    
    mover_type = request.args.get('type', 'both')
    limit = min(int(request.args.get('limit', 10)), 50)
    
    result = {}
    
    if mover_type in ('gainers', 'both'):
        gainers = get_day_gainers(limit=limit)
        # Format consistent with frontend expectation
        result['gainers'] = [{
            'symbol': g.get('symbol'),
            'name': g.get('name'),
            'price': float(g['price']) if g.get('price') else None,
            'change': float(g['change']) if g.get('change') else None,
            'changePercent': float(g['changePercent']) if g.get('changePercent') else None,
            'volume': g.get('volume'),
            'assetType': 'stock'
        } for g in gainers]
        
    if mover_type in ('losers', 'both'):
        losers = get_day_losers(limit=limit)
        result['losers'] = [{
            'symbol': l.get('symbol'),
            'name': l.get('name'),
            'price': float(l['price']) if l.get('price') else None,
            'change': float(l['change']) if l.get('change') else None,
            'changePercent': float(l['changePercent']) if l.get('changePercent') else None,
            'volume': l.get('volume'),
            'assetType': 'stock'
        } for l in losers]
        
    return jsonify(result)


@live_bp.route('/most-active', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_MOVERS, query_string=True)
def get_live_most_active():
    """Get most active stocks live"""
    limit = min(safe_int(request.args.get('limit'), default=10), 50)

    # Try live screener first
    try:
        from handlers.market_data.screener_handler import get_most_active
        active = get_most_active(limit=limit)
        if active:
            return jsonify([{
                'symbol': a.get('symbol'),
                'name': a.get('name'),
                'price': float(a['price']) if a.get('price') else None,
                'change': float(a['change']) if a.get('change') else None,
                'changePercent': float(a['changePercent']) if a.get('changePercent') else None,
                'volume': a.get('volume'),
                'assetType': 'stock'
            } for a in active])
    except Exception as e:
        logger.warning(f"Most-active screener failed: {e}")

    # Fallback: use MarketData table sorted by volume
    try:
        from models.market import MarketData
        stocks = MarketData.query.filter(
            MarketData.volume.isnot(None),
            MarketData.volume > 0,
            MarketData.asset_type != 'crypto'
        ).order_by(MarketData.volume.desc()).limit(limit).all()

        return jsonify([{
            'symbol': s.symbol,
            'name': s.name,
            'price': float(s.price) if s.price else None,
            'change': float(s.change) if s.change else None,
            'changePercent': float(s.change_percent) if s.change_percent else None,
            'volume': s.volume,
            'assetType': 'stock'
        } for s in stocks])
    except Exception as e:
        logger.error(f"Most-active DB fallback error: {e}")
        return jsonify([])


# ---------------------------------------------------------------------------
# Sector Performance Heatmap
# ---------------------------------------------------------------------------

@live_bp.route('/sector-performance', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_sector_performance():
    """
    Sector performance heatmap data.
    Aggregates from the MarketData table (no extra yfinance calls).
    """
    try:
        from sqlalchemy import func
        from models.market import MarketData

        # Query stocks grouped by sector
        stocks = MarketData.query.filter(
            MarketData.sector.isnot(None),
            MarketData.sector != '',
            MarketData.change_percent.isnot(None)
        ).all()

        if not stocks:
            return jsonify([])

        # Aggregate by sector
        sector_map = {}
        for s in stocks:
            sec = s.sector
            if sec not in sector_map:
                sector_map[sec] = {
                    'name': sec,
                    'stocks': [],
                    'total_change': 0,
                    'total_market_cap': 0,
                    'count': 0,
                }
            sector_map[sec]['stocks'].append(s)
            sector_map[sec]['total_change'] += float(s.change_percent or 0)
            sector_map[sec]['total_market_cap'] += float(s.market_cap or 0)
            sector_map[sec]['count'] += 1

        sectors = []
        for sec_name, info in sector_map.items():
            if info['count'] == 0:
                continue

            avg_change = info['total_change'] / info['count']

            # Find top gainer and loser in this sector
            sorted_stocks = sorted(info['stocks'],
                                   key=lambda x: float(x.change_percent or 0),
                                   reverse=True)
            top_gainer = sorted_stocks[0] if sorted_stocks else None
            top_loser = sorted_stocks[-1] if len(sorted_stocks) > 1 else None

            sectors.append({
                'name': sec_name,
                'avgChangePercent': round(avg_change, 2),
                'totalMarketCap': info['total_market_cap'],
                'stockCount': info['count'],
                'topGainer': {
                    'symbol': top_gainer.symbol,
                    'changePercent': round(float(top_gainer.change_percent or 0), 2),
                } if top_gainer else None,
                'topLoser': {
                    'symbol': top_loser.symbol,
                    'changePercent': round(float(top_loser.change_percent or 0), 2),
                } if top_loser else None,
            })

        # Sort by market cap descending for visual weight
        sectors.sort(key=lambda x: x['totalMarketCap'], reverse=True)

        return jsonify(sectors)

    except Exception as e:
        logger.error(f"Sector performance error: {e}")
        return jsonify([])


# ---------------------------------------------------------------------------
# Earnings Calendar (Public)
# ---------------------------------------------------------------------------

@live_bp.route('/earnings-calendar', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_earnings_calendar():
    """
    Public earnings calendar - upcoming and recent earnings reports.
    """
    try:
        from models import EarningsCalendar
        from datetime import date, timedelta

        limit = safe_int(request.args.get('limit'), default=20)
        days = safe_int(request.args.get('days'), default=14)

        today = date.today()
        start_date = today - timedelta(days=3)  # Include recent past
        end_date = today + timedelta(days=days)

        events = EarningsCalendar.query.filter(
            EarningsCalendar.earnings_date >= start_date,
            EarningsCalendar.earnings_date <= end_date,
        ).order_by(EarningsCalendar.earnings_date.asc()).limit(limit).all()

        if events:
            return jsonify([{
                'symbol': e.symbol,
                'companyName': e.company_name,
                'earningsDate': e.earnings_date.isoformat() if e.earnings_date else None,
                'epsEstimate': float(e.eps_estimate) if e.eps_estimate else None,
                'epsActual': float(e.eps_actual) if e.eps_actual else None,
                'surprisePercent': float(e.surprise_percent) if e.surprise_percent else None,
                'revenueEstimate': e.revenue_estimate,
                'revenueActual': e.revenue_actual,
                'marketCap': e.market_cap,
                'timing': e.before_after_market,
            } for e in events])
        
        # Fallback to live YFinance if DB is empty
        from handlers.market_data.calendar_handler import get_earnings_calendar as fetch_live_earnings
        live_data = fetch_live_earnings(start=start_date.isoformat(), end=end_date.isoformat(), limit=limit)
        return jsonify(live_data)

    except Exception as e:
        logger.error(f"Earnings calendar error: {e}")
        return jsonify([])


# ---------------------------------------------------------------------------
# Advanced Forex Analytics
# ---------------------------------------------------------------------------

CACHE_TIMEOUT_CORRELATION = 1800  # 30 min – correlations change slowly


@live_bp.route('/forex/strength', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_DEFAULT, query_string=True)
def get_forex_strength():
    """Currency Strength Index – real cross-pair aggregation."""
    from handlers.market_data.forex_analytics_handler import compute_currency_strength
    try:
        return jsonify(compute_currency_strength())
    except Exception as e:
        logger.error(f"Forex strength error: {e}")
        return jsonify({'error': str(e)}), 500


@live_bp.route('/forex/correlation', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_CORRELATION, query_string=True)
def get_forex_correlation():
    """Cross-pair Pearson correlation matrix from historical prices."""
    from handlers.market_data.forex_analytics_handler import compute_correlation_matrix
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    try:
        return jsonify(compute_correlation_matrix(period=period, interval=interval))
    except Exception as e:
        logger.error(f"Forex correlation error: {e}")
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------------------------------
# Floorsheet – real intraday trade data
# ---------------------------------------------------------------------------

@live_bp.route('/floorsheet', methods=['GET'])
@cache.cached(timeout=CACHE_TIMEOUT_LIVE, query_string=True)
def get_live_floorsheet():
    """Market transaction floorsheet. DB-first, yfinance fallback."""
    from handlers.market_data.floorsheet_handler import (
        get_floorsheet_from_db,
        fetch_live_floorsheet,
    )

    limit = min(safe_int(request.args.get('limit'), 100), 500)
    symbol = request.args.get('symbol', '').strip().upper() or None

    # Path A: DB (fast)
    db_data = get_floorsheet_from_db(symbol=symbol, limit=limit)
    if db_data:
        return jsonify({
            'trades': db_data,
            'source': 'database',
            'timestamp': datetime.utcnow().isoformat(),
        })

    # Path B: Live yfinance
    try:
        return jsonify(fetch_live_floorsheet(symbol=symbol, limit=limit))
    except Exception as e:
        logger.error(f"Floorsheet error: {e}")
        return jsonify({
            'trades': [],
            'source': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat(),
        }), 500

