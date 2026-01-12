"""
Portfolio API Routes
Endpoints for user watchlists and portfolios
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
import uuid
from routes.decorators import auth_required
from models import db, Watchlist, WatchlistItem, UserPortfolio, PortfolioHolding, MarketData

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/watchlist', methods=['GET'])
@auth_required
def get_watchlist():
    """Get user's default watchlist items"""
    # load user's default watchlist from DB
    watchlist = Watchlist.query.filter_by(user_id=request.user.id, is_default=True).first()
    symbols = []
    if watchlist:
        items = WatchlistItem.query.filter_by(watchlist_id=watchlist.id).all()
        symbols = [i.symbol for i in items]

    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        # no header -> default to US only
        filter_condition = (MarketData.country_code == 'US')
    else:
        country = header_country.strip().upper()
        if country == 'GLOBAL':
            filter_condition = (MarketData.country_code == 'GLOBAL')
        else:
            filter_condition = (MarketData.country_code == country)

    if not symbols:
        return jsonify([])

    stocks = MarketData.query.filter(
        MarketData.symbol.in_(symbols),
        MarketData.asset_type == 'stock',
        filter_condition
    ).all()

    # map market data by symbol for robust response even when some symbols lack market rows
    market_map = {m.symbol: m for m in stocks}

    result = []
    for i, sym in enumerate(symbols):
        m = market_map.get(sym)
        if m:
            result.append({
                'id': i + 1,
                'symbol': m.symbol,
                'name': m.name,
                'price': float(m.price) if m.price else 0,
                'change': float(m.change) if m.change else 0,
                'changePercent': float(m.change_percent) if m.change_percent else 0,
                'addedAt': m.last_updated.isoformat() if m.last_updated else None
            })
        else:
            result.append({
                'id': i + 1,
                'symbol': sym,
                'name': None,
                'price': None,
                'change': None,
                'changePercent': None,
                'addedAt': None
            })

    return jsonify(result)


@portfolio_bp.route('/watchlist', methods=['POST'])
@auth_required
def add_to_watchlist():
    """Add stock to watchlist"""
    data = request.get_json()
    symbol = data.get('symbol')
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400

    symbol = symbol.strip().upper()

    # find or create user's default watchlist
    watchlist = Watchlist.query.filter_by(user_id=request.user.id, is_default=True).first()
    if not watchlist:
        watchlist = Watchlist(id=str(uuid.uuid4()), user_id=request.user.id, name='Default Watchlist', is_default=True)
        db.session.add(watchlist)
        db.session.commit()

    # avoid duplicates
    existing = WatchlistItem.query.filter_by(watchlist_id=watchlist.id, symbol=symbol).first()
    if existing:
        return jsonify({'message': f'{symbol} already in watchlist'}), 200

    item = WatchlistItem(watchlist_id=watchlist.id, symbol=symbol)
    db.session.add(item)
    db.session.commit()

    return jsonify({'message': f'{symbol} added to watchlist', 'id': item.id})


@portfolio_bp.route('/watchlist/<symbol>', methods=['DELETE'])
@auth_required
def remove_from_watchlist(symbol):
    """Remove stock from watchlist"""
    symbol = symbol.strip().upper()
    watchlist = Watchlist.query.filter_by(user_id=request.user.id, is_default=True).first()
    if not watchlist:
        return jsonify({'error': 'Watchlist not found'}), 404

    item = WatchlistItem.query.filter_by(watchlist_id=watchlist.id, symbol=symbol).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': f'{symbol} removed from watchlist'})


@portfolio_bp.route('/watchlists', methods=['GET'])
@auth_required
def get_watchlists():
    """Get all user watchlists"""
    watchlists = Watchlist.query.filter_by(user_id=request.user.id).limit(10).all()

    result = []
    for w in watchlists:
        items = WatchlistItem.query.filter_by(watchlist_id=w.id).all()
        result.append({
            'id': w.id,
            'name': w.name,
            'items': [i.symbol for i in items],
            'createdAt': w.created_at.isoformat() if w.created_at else None
        })

    return jsonify(result)


@portfolio_bp.route('/list', methods=['GET'])
@auth_required
def get_portfolios():
    """Get user's portfolios"""
    portfolios = UserPortfolio.query.limit(5).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'totalValue': float(p.total_value) if p.total_value else 0,
        'totalGain': 0,
        'totalGainPercent': 0,
        'holdings': []
    } for p in portfolios])


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@auth_required
def get_portfolio(portfolio_id):
    """Get portfolio by ID"""
    portfolio = UserPortfolio.query.get_or_404(portfolio_id)
    
    return jsonify({
        'id': portfolio.id,
        'name': portfolio.name,
        'totalValue': float(portfolio.total_value) if portfolio.total_value else 0,
        'holdings': []
    })


@portfolio_bp.route('', methods=['POST'])
@auth_required
def create_portfolio():
    """Create new portfolio"""
    data = request.get_json()
    name = data.get('name', 'My Portfolio')
    # persist portfolio to DB
    new_id = str(uuid.uuid4())
    portfolio = UserPortfolio(id=new_id, user_id=request.user.id, name=name)
    db.session.add(portfolio)
    db.session.commit()

    return jsonify({
        'id': portfolio.id,
        'name': portfolio.name,
        'totalValue': float(portfolio.total_value) if portfolio.total_value else 0,
        'holdings': []
    }), 201
