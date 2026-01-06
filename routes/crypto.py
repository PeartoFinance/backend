"""
Crypto API Routes with SQLAlchemy
- Markets, global data, coin details, history
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models.db import db, MarketPrice, CryptoMarketData

crypto_bp = Blueprint('crypto', __name__)


@crypto_bp.route('/markets', methods=['GET'])
def get_markets():
    """Get cryptocurrency market listings"""
    limit = min(int(request.args.get('limit', 100)), 250)
    page = max(int(request.args.get('page', 1)), 1)
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
    
    cryptos = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto'
    ).order_by(desc(sort_column)).offset(offset).limit(limit).all()
    
    return jsonify([c.to_dict() for c in cryptos])


@crypto_bp.route('/global', methods=['GET'])
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
def get_coin(symbol):
    """Get single cryptocurrency details"""
    crypto = MarketPrice.query.filter(
        MarketPrice.symbol == symbol.upper(),
        MarketPrice.asset_type == 'crypto'
    ).first()
    
    if not crypto:
        return jsonify({'error': 'Cryptocurrency not found'}), 404
    
    return jsonify(crypto.to_dict())


@crypto_bp.route('/coins', methods=['GET'])
def get_coins():
    """Get multiple coins by symbols"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    cryptos = MarketPrice.query.filter(
        MarketPrice.symbol.in_(symbols),
        MarketPrice.asset_type == 'crypto'
    ).all()
    
    return jsonify([c.to_dict() for c in cryptos])


@crypto_bp.route('/gainers', methods=['GET'])
def get_gainers():
    """Get top gaining cryptocurrencies"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    gainers = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto',
        MarketPrice.change_percent > 0
    ).order_by(desc(MarketPrice.change_percent)).limit(limit).all()
    
    return jsonify([g.to_dict() for g in gainers])


@crypto_bp.route('/losers', methods=['GET'])
def get_losers():
    """Get top losing cryptocurrencies"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    losers = MarketPrice.query.filter(
        MarketPrice.asset_type == 'crypto',
        MarketPrice.change_percent < 0
    ).order_by(MarketPrice.change_percent).limit(limit).all()
    
    return jsonify([l.to_dict() for l in losers])
