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
    """Get real-time quote for a single symbol - optimized for polling"""
    global live_quote_cache
    
    symbol = symbol.upper()
    now = time.time()
    
    # Check memory cache first (10 second cache)
    cache_key = f"live_{symbol}"
    if cache_key in live_quote_cache:
        cache_time, cached_data = live_quote_cache[cache_key]
        if now - cache_time < 10:
            cached_data['cached'] = True
            return jsonify(cached_data)
    
    # Query database
    stock = MarketData.query.filter_by(symbol=symbol).first()
    
    if not stock:
        # Try auto-import for unknown symbols
        try:
            from handlers.market_data.stock_handler import import_stocks_to_db
            import_stocks_to_db([symbol], country_code='GLOBAL')
            stock = MarketData.query.filter_by(symbol=symbol).first()
        except Exception as e:
            print(f"Live quote import error {symbol}: {e}")
    
    if not stock:
        return jsonify({'error': 'Symbol not found'}), 404
    
    data = {
        'symbol': stock.symbol,
        'name': stock.name,
        'price': float(stock.price) if stock.price else None,
        'change': float(stock.change) if stock.change else None,
        'changePercent': float(stock.change_percent) if stock.change_percent else None,
        'dayHigh': float(stock.day_high) if stock.day_high else None,
        'dayLow': float(stock.day_low) if stock.day_low else None,
        'volume': stock.volume,
        'open': float(stock.open_price) if stock.open_price else None,
        'previousClose': float(stock.previous_close) if stock.previous_close else None,
        'lastUpdated': stock.last_updated.isoformat() if stock.last_updated else None,
        'assetType': stock.asset_type,
        'cached': False
    }
    
    # Save to cache
    live_quote_cache[cache_key] = (now, data)
    
    return jsonify(data)


@live_bp.route('/quotes', methods=['GET'])
def get_live_quotes():
    """Get real-time quotes for multiple symbols"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',') if s.strip()]
    
    if len(symbols) > 10:
        return jsonify({'error': 'Maximum 10 symbols allowed'}), 400
    
    stocks = MarketData.query.filter(MarketData.symbol.in_(symbols)).all()
    
    results = []
    for stock in stocks:
        results.append({
            'symbol': stock.symbol,
            'name': stock.name,
            'price': float(stock.price) if stock.price else None,
            'change': float(stock.change) if stock.change else None,
            'changePercent': float(stock.change_percent) if stock.change_percent else None,
            'volume': stock.volume,
            'assetType': stock.asset_type
        })
    
    return jsonify(results)


@live_bp.route('/intraday/<symbol>', methods=['GET'])
def get_live_intraday(symbol):
    """
    Get recent intraday data for live charts.
    Returns 1-minute data for the last 30-60 minutes.
    Uses aggressive caching to prevent rate limiting.
    """
    from handlers.market_data.stock_handler import get_stock_history
    
    symbol = symbol.upper()
    now = time.time()
    
    # Check memory cache (30 second cache for intraday)
    cache_key = f"intraday_{symbol}"
    if cache_key in live_quote_cache:
        cache_time, cached_data = live_quote_cache[cache_key]
        if now - cache_time < 30:
            return jsonify({
                'symbol': symbol,
                'interval': '1m',
                'data': cached_data,
                'cached': True
            })
    
    try:
        # Get last 1 day of 1-minute data
        history = get_stock_history(symbol, period='1d', interval='1m')
        
        if not history:
            return jsonify({'error': 'No intraday data available'}), 404
        
        # Cache the result
        live_quote_cache[cache_key] = (now, history)
        
        return jsonify({
            'symbol': symbol,
            'interval': '1m',
            'data': history,
            'cached': False
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@live_bp.route('/market-pulse', methods=['GET'])
def get_market_pulse():
    """
    Get quick market overview for live dashboard.
    Returns major indices and top movers.
    """
    from sqlalchemy import desc, asc
    
    # Top gainers (limit 5)
    gainers = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        MarketData.change_percent > 0
    ).order_by(desc(MarketData.change_percent)).limit(5).all()
    
    # Top losers (limit 5)
    losers = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        MarketData.change_percent < 0
    ).order_by(asc(MarketData.change_percent)).limit(5).all()
    
    # Most active (limit 5)
    active = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        MarketData.volume != None
    ).order_by(desc(MarketData.volume)).limit(5).all()
    
    def to_mini_dict(stock):
        return {
            'symbol': stock.symbol,
            'name': stock.name,
            'price': float(stock.price) if stock.price else None,
            'changePercent': float(stock.change_percent) if stock.change_percent else None
        }
    
    return jsonify({
        'gainers': [to_mini_dict(g) for g in gainers],
        'losers': [to_mini_dict(l) for l in losers],
        'mostActive': [to_mini_dict(a) for a in active],
        'timestamp': datetime.utcnow().isoformat()
    })
