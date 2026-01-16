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

    # Track watchlist add activity
    try:
        from handlers import track_watchlist_add
        track_watchlist_add(request.user.id, symbol)
    except Exception as e:
        print(f'[Portfolio] Activity tracking failed: {e}')

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

    # Track watchlist remove activity
    try:
        from handlers import track_watchlist_remove
        track_watchlist_remove(request.user.id, symbol)
    except Exception as e:
        print(f'[Portfolio] Activity tracking failed: {e}')

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
    """Get user's portfolios with holdings"""
    portfolios = UserPortfolio.query.filter_by(user_id=request.user.id).all()
    
    result = []
    for p in portfolios:
        # Get holdings for this portfolio
        holdings = PortfolioHolding.query.filter_by(portfolio_id=p.id).all()
        
        # Calculate totals from holdings
        total_value = sum(float(h.current_value or 0) for h in holdings)
        total_gain = sum(float(h.gain_loss or 0) for h in holdings)
        total_cost = sum(float(h.shares or 0) * float(h.avg_buy_price or 0) for h in holdings)
        total_gain_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
        
        result.append({
            'id': p.id,
            'name': p.name,
            'totalValue': total_value,
            'totalGain': total_gain,
            'totalGainPercent': round(total_gain_percent, 2),
            'holdings': [_holding_to_dict(h) for h in holdings]
        })
    
    return jsonify(result)


def _holding_to_dict(h):
    """Convert holding to frontend-compatible dict"""
    shares = float(h.shares or 0)
    avg_cost = float(h.avg_buy_price or 0)
    current_price = float(h.current_price or 0)
    total_value = shares * current_price
    total_cost = shares * avg_cost
    gain = total_value - total_cost
    gain_percent = (gain / total_cost * 100) if total_cost > 0 else 0
    
    return {
        'id': h.id,
        'symbol': h.symbol,
        'name': h.symbol,  # Will be enriched from MarketData if needed
        'shares': shares,
        'avgCost': avg_cost,
        'currentPrice': current_price,
        'totalValue': round(total_value, 2),
        'gain': round(gain, 2),
        'gainPercent': round(gain_percent, 2)
    }


@portfolio_bp.route('/<portfolio_id>', methods=['GET'])
@auth_required
def get_portfolio(portfolio_id):
    """Get portfolio by ID with holdings"""
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    # Get holdings
    holdings = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id).all()
    
    # Calculate totals
    total_value = sum(float(h.current_value or 0) for h in holdings)
    total_gain = sum(float(h.gain_loss or 0) for h in holdings)
    total_cost = sum(float(h.shares or 0) * float(h.avg_buy_price or 0) for h in holdings)
    total_gain_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
    
    return jsonify({
        'id': portfolio.id,
        'name': portfolio.name,
        'totalValue': total_value,
        'totalGain': total_gain,
        'totalGainPercent': round(total_gain_percent, 2),
        'holdings': [_holding_to_dict(h) for h in holdings]
    })


@portfolio_bp.route('', methods=['POST'])
@auth_required
def create_portfolio():
    """Create new portfolio"""
    data = request.get_json()
    name = data.get('name', 'My Portfolio')
    new_id = str(uuid.uuid4())
    portfolio = UserPortfolio(id=new_id, user_id=request.user.id, name=name)
    db.session.add(portfolio)
    db.session.commit()

    return jsonify({
        'id': portfolio.id,
        'name': portfolio.name,
        'totalValue': 0,
        'totalGain': 0,
        'totalGainPercent': 0,
        'holdings': []
    }), 201


@portfolio_bp.route('/<portfolio_id>/holdings', methods=['POST'])
@auth_required
def add_holding(portfolio_id):
    """Add holding to portfolio"""
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    shares = float(data.get('shares', 0))
    avg_buy_price = float(data.get('avgBuyPrice', 0))
    
    if not symbol or shares <= 0:
        return jsonify({'error': 'Symbol and shares required'}), 400
    
    # Get current market price
    market = MarketData.query.filter_by(symbol=symbol).first()
    current_price = float(market.price) if market and market.price else avg_buy_price
    
    # Calculate values
    current_value = shares * current_price
    gain_loss = current_value - (shares * avg_buy_price)
    gain_percent = (gain_loss / (shares * avg_buy_price) * 100) if avg_buy_price > 0 else 0
    
    holding = PortfolioHolding(
        id=str(uuid.uuid4()),
        portfolio_id=portfolio_id,
        symbol=symbol,
        shares=shares,
        avg_buy_price=avg_buy_price,
        current_price=current_price,
        current_value=current_value,
        gain_loss=gain_loss,
        gain_loss_percent=gain_percent
    )
    
    db.session.add(holding)
    db.session.commit()
    
    # Track activity
    try:
        from handlers import track_activity
        track_activity(request.user.id, 'holding_added', 'portfolio', entity_id=holding.id, extra_data={'symbol': symbol, 'shares': shares})
    except Exception as e:
        print(f'[Portfolio] Activity tracking failed: {e}')
    
    return jsonify({
        'id': holding.id,
        'message': f'{symbol} added to portfolio',
        'holding': _holding_to_dict(holding)
    }), 201


@portfolio_bp.route('/<portfolio_id>/holdings/<holding_id>', methods=['DELETE'])
@auth_required
def delete_holding(portfolio_id, holding_id):
    """Delete holding from portfolio"""
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    holding = PortfolioHolding.query.filter_by(id=holding_id, portfolio_id=portfolio_id).first()
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    symbol = holding.symbol
    db.session.delete(holding)
    db.session.commit()
    
    # Track activity
    try:
        from handlers import track_activity
        track_activity(request.user.id, 'holding_removed', 'portfolio', entity_id=holding_id, extra_data={'symbol': symbol})
    except Exception as e:
        print(f'[Portfolio] Activity tracking failed: {e}')
    
    return jsonify({'message': f'{symbol} removed from portfolio'})
