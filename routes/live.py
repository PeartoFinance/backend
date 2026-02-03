"""
Live Data API Routes
Real-time quotes and intraday data for live chart updates
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from extensions import cache
from models.market import MarketData
import time

live_bp = Blueprint('live', __name__)

# In-memory cache for live quotes (10 second TTL)
live_quote_cache = {}


@live_bp.route('/quote/<symbol>', methods=['GET'])
def get_live_quote(symbol):
    """Get real-time quote for a single symbol using direct handlers"""
    symbol = symbol.upper()
    
    # Try stock handler first (covers most including ETFs)
    from handlers.market_data.stock_handler import get_stock_quote
    from handlers.market_data.crypto_handler import get_crypto_quote
    
    # Simple heuristic: if it contains '-', likely crypto (e.g., BTC-USD)
    data = None
    if '-' in symbol:
        data = get_crypto_quote(symbol)
    
    if not data:
        data = get_stock_quote(symbol)
        
    if not data:
        # Fallback check if it was crypto but didn't have dash? Unlikely for YF but possible
        if '-' not in symbol:
            data = get_crypto_quote(symbol)

    if not data:
        return jsonify({'error': 'Symbol not found'}), 404
    
    # Ensure assetType is present
    if not data.get('assetType'):
        # Infer from data or defaults
        if data.get('quoteType') == 'CRYPTOCURRENCY' or data.get('sector') == 'Cryptocurrency':
            data['assetType'] = 'crypto'
        else:
            data['assetType'] = 'stock'

    # Ensure numeric fields are floats
    if data.get('price'): data['price'] = float(data['price'])
    if data.get('change'): data['change'] = float(data['change'])
    if data.get('changePercent'): 
        # YFinance sometimes returns 0.05 for 5%, sometimes 5.0. 
        # Usually it's raw scalar e.g. 0.015 for 1.5% in some versions, or 1.5. 
        # Just passing it through, frontend handles it.
        data['changePercent'] = float(data['changePercent'])
        
    return jsonify(data)


@live_bp.route('/quotes', methods=['GET'])
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
    
    # Enrich with assetType
    for item in results:
        if not item.get('assetType'):
             if item.get('quoteType') == 'CRYPTOCURRENCY' or item.get('sector') == 'Cryptocurrency':
                 item['assetType'] = 'crypto'
             else:
                 item['assetType'] = 'stock'
    
    return jsonify(results)


@live_bp.route('/intraday/<symbol>', methods=['GET'])
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
def get_market_pulse():
    """
    Get quick market overview for live dashboard via direct handlers.
    Returns major indices and top movers.
    """
    from handlers.market_data.screener_handler import get_day_gainers, get_day_losers, get_most_active
    
    try:
        # Fetch directly from external source via handlers
        # Using limit=5 as per UI requirement
        gainers = get_day_gainers(limit=5)
        losers = get_day_losers(limit=5)
        active = get_most_active(limit=5)
        
        # Helper to format handler output for frontend
        def format_item(item):
            price = item.get('price')
            change_p = item.get('changePercent')
            if price: price = float(price)
            if change_p: change_p = float(change_p)
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': price,
                'changePercent': change_p
            }
        
        return jsonify({
            'gainers': [format_item(g) for g in gainers],
            'losers': [format_item(l) for l in losers],
            'mostActive': [format_item(a) for a in active],
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@live_bp.route('/search', methods=['GET'])
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
            return {
                'symbol': item.get('symbol'),
                'name': item.get('displayName') or item.get('name'), # index handler adds displayName
                'price': float(price) if price else None,
                'change': float(change) if change else None,
                'changePercent': float(change_p) if change_p else None,
                'assetType': 'index'
            }

        def format_comm(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': float(price) if price else None,
                'change': float(change) if change else None,
                'changePercent': float(change_p) if change_p else None,
                'assetType': 'commodity',
                'unit': item.get('unit')
            }
            
        def format_stock(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            vol = item.get('volume')
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': float(price) if price else None,
                'change': float(change) if change else None,
                'changePercent': float(change_p) if change_p else None,
                'assetType': 'stock',
                'volume': vol
            }
            
        def format_crypto(item):
            price = item.get('price')
            change = item.get('change')
            change_p = item.get('changePercent')
            return {
                'symbol': item.get('symbol'),
                'name': item.get('name'),
                'price': float(price) if price else None,
                'change': float(change) if change else None,
                'changePercent': float(change_p) if change_p else None,
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
        return jsonify({'error': str(e)}), 500
