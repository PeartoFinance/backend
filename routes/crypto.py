"""
Crypto API Routes with SQLAlchemy
- Markets, global data, coin details, history
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models import db, MarketData as MarketPrice, CryptoMarketData
from extensions import cache
from utils.validators import safe_int

crypto_bp = Blueprint('crypto', __name__)


@crypto_bp.route('/markets', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_markets():
    """Get cryptocurrency market listings"""
    # Safe conversion: Returns 100 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 100), 250)
    # Safe conversion: Returns page 1 if invalid characters sent
    page = max(safe_int(request.args.get('page'), 1), 1)
    sort_by = request.args.get('sort', 'market_cap')
    
    offset = (page - 1) * limit
    
    # Map sort options to columns
    sort_map = {
        'market_cap': MarketPrice.market_cap,
        'price': MarketPrice.price,
        'change': MarketPrice.change_percent,
        'volume': MarketPrice.volume
    }
    sort_column = sort_map.get(sort_by, MarketPrice.market_cap)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = MarketPrice.country_code.in_([hc, 'GLOBAL'])
    else:
        country_filter = (MarketPrice.country_code == 'GLOBAL')

    cryptos = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto',
        country_filter
    ).order_by(desc(sort_column)).offset(offset).limit(limit).all()
    
    return jsonify([c.to_dict() for c in cryptos])


@crypto_bp.route('/global', methods=['GET'])
@cache.cached(timeout=60)
def get_global():
    """Get global cryptocurrency market metrics"""
    data = CryptoMarketData.query.order_by(
        desc(CryptoMarketData.last_updated)
    ).first()
    
    if not data:
        return jsonify({
            'totalMarketCap': None,
            'totalVolume24h': None,
            'btcDominance': None,
            'ethDominance': None,
            'activeCryptocurrencies': None,
            'activeExchanges': None
        })
    
    return jsonify(data.to_dict())


@crypto_bp.route('/coin/<symbol>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_coin(symbol):
    """Get single cryptocurrency details"""
    from handlers.market_data.crypto_handler import import_crypto_to_db

    symbol = symbol.upper()
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = MarketPrice.country_code.in_([hc, 'GLOBAL'])
    else:
        country_filter = (MarketPrice.country_code == 'GLOBAL')

    crypto = MarketPrice.query.filter(
        MarketPrice.symbol == symbol,
        MarketPrice.asset_type == 'crypto',
        country_filter
    ).first()
    
    # Auto-discovery if not found
    if not crypto:
        try:
            success = import_crypto_to_db(symbol)
            if success:
                crypto = MarketPrice.query.filter(
                    MarketPrice.symbol == symbol,
                    MarketPrice.asset_type == 'crypto',
                    country_filter
                ).first()
        except Exception as e:
            print(f"Error auto-importing crypto {symbol}: {e}")

    if not crypto:
        return jsonify({'error': 'Cryptocurrency not found'}), 404
    
    return jsonify(crypto.to_dict())


# In-memory cache for historical data (Speed optimization)
history_cache = {}

@crypto_bp.route('/history/<symbol>', methods=['GET'])
def get_history(symbol):
    """Get cryptocurrency historical data"""
    from handlers.market_data.crypto_handler import get_crypto_history
    import time
    
    symbol = symbol.upper()
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    
    # SMART VALIDATION: Yahoo Finance intraday limits (1m = max 7 days)
    if interval == '1m' and period not in ('1d', '5d', '7d'):
        period = '1d' # Ensure 1-min charts load by defaulting to 1-day period
    elif interval in ('2m', '5m', '15m', '30m', '90m') and period not in ('1d', '5d', '1mo'):
        if 'y' in period or 'max' in period:
            period = '1mo'
    
    # 1. Check In-Memory Cache first (Consistent with stocks.py performance)
    cache_key = f"{symbol}_{period}_{interval}"
    now = time.time()
    if cache_key in history_cache:
        cache_time, cached_data = history_cache[cache_key]
        if now - cache_time < 300:  # 5 minute cache
            return jsonify({
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'data': cached_data,
                'source': 'memory_cache'
            })
            
    try:
        history = get_crypto_history(symbol, period=period, interval=interval)
        
        # Save to memory cache for next user
        if history:
            history_cache[cache_key] = (now, history)
            
        return jsonify({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@crypto_bp.route('/coins', methods=['GET'])
def get_coins():
    """Get multiple coins by symbols"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = MarketPrice.country_code.in_([hc, 'GLOBAL'])
    else:
        country_filter = (MarketPrice.country_code == 'GLOBAL')

    cryptos = MarketPrice.query.filter(
        MarketPrice.symbol.in_(symbols),
        MarketPrice.asset_type == 'crypto',
        country_filter
    ).all()
    
    return jsonify([c.to_dict() for c in cryptos])


@crypto_bp.route('/gainers', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_gainers():
    """Get top gaining cryptocurrencies"""
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = MarketPrice.country_code.in_([hc, 'GLOBAL'])
    else:
        country_filter = (MarketPrice.country_code == 'GLOBAL')

    gainers = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto',
        MarketPrice.change_percent > 0,
        country_filter
    ).order_by(desc(MarketPrice.change_percent)).limit(limit).all()
    
    return jsonify([g.to_dict() for g in gainers])


@crypto_bp.route('/losers', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_losers():
    """Get top losing cryptocurrencies"""
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        country_filter = MarketPrice.country_code.in_([hc, 'GLOBAL'])
    else:
        country_filter = (MarketPrice.country_code == 'GLOBAL')

    losers = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto',
        MarketPrice.change_percent < 0,
        country_filter
    ).order_by(MarketPrice.change_percent).limit(limit).all()
    
    return jsonify([l.to_dict() for l in losers])
