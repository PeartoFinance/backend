"""
Stocks API Routes with SQLAlchemy
- Quotes, search, profile, history, movers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc, func
from datetime import datetime, timedelta
from models.base import db
from models.market import MarketData

stocks_bp = Blueprint('stocks', __name__)


@stocks_bp.route('/quotes', methods=['GET'])
def get_quotes():
    """Get real-time quotes for multiple symbols"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]
    
    prices = MarketData.query.filter(
        MarketData.symbol.in_(symbols),
        MarketData.asset_type == 'stock'
    ).all()
    
    return jsonify([p.to_dict() for p in prices])


@stocks_bp.route('/search', methods=['GET'])
def search_stocks():
    """Search stocks by name or symbol"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)
    
    if not query:
        return jsonify({'error': 'q parameter required'}), 400
    
    stocks = MarketData.query.filter(
        db.or_(
            MarketData.symbol.ilike(f'%{query}%'),
            MarketData.name.ilike(f'%{query}%')
        ),
        MarketData.asset_type == 'stock'
    ).limit(limit).all()
    
    return jsonify([{
        'symbol': s.symbol,
        'name': s.name,
        'exchange': s.exchange,
        'type': s.asset_type
    } for s in stocks])


@stocks_bp.route('/profile/<symbol>', methods=['GET'])
def get_profile(symbol):
    """Get basic stock profile from market data"""
    stock = MarketData.query.filter(
        MarketData.symbol == symbol.upper(),
        MarketData.asset_type == 'stock'
    ).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    return jsonify(stock.to_dict())


@stocks_bp.route('/movers', methods=['GET'])
def get_movers():
    """Get top gainers and losers"""
    mover_type = request.args.get('type', 'both')
    limit = min(int(request.args.get('limit', 10)), 50)
    
    result = {}
    
    if mover_type in ('gainers', 'both'):
        gainers = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent > 0
        ).order_by(desc(MarketData.change_percent)).limit(limit).all()
        result['gainers'] = [g.to_dict() for g in gainers]
    
    if mover_type in ('losers', 'both'):
        losers = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent < 0
        ).order_by(asc(MarketData.change_percent)).limit(limit).all()
        result['losers'] = [l.to_dict() for l in losers]
    
    return jsonify(result)


@stocks_bp.route('/most-active', methods=['GET'])
def get_most_active():
    """Get most actively traded stocks"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    stocks = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.volume != None
    ).order_by(desc(MarketData.volume)).limit(limit).all()
    
    return jsonify([{
        'symbol': s.symbol,
        'name': s.name,
        'price': float(s.price) if s.price else None,
        'volume': s.volume
    } for s in stocks])
