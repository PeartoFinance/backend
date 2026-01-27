"""
Portfolio API Routes
Endpoints for user watchlists and portfolios
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
import uuid
from routes.decorators import auth_required
from models import db, Watchlist, WatchlistItem, UserPortfolio, PortfolioHolding, MarketData, UserInvestmentGoal
from services.portfolio_service import calculate_portfolio_health

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/analysis/health-score', methods=['GET'])
@auth_required
def get_portfolio_health_score():
    """Calculate and return the user's portfolio health score"""
    result = calculate_portfolio_health(request.user.id)
    return jsonify(result)


@portfolio_bp.route('/goals', methods=['GET'])
@auth_required
def get_portfolio_goals():
    """Get user's investment goals"""
    goals = UserInvestmentGoal.query.filter_by(user_id=request.user.id).first()
    if not goals:
        # Return defaults if not set
        return jsonify({
            'target_stocks_percent': 60,
            'target_bonds_percent': 20,
            'target_cash_percent': 10,
            'target_crypto_percent': 5,
            'target_commodities_percent': 5,
            'risk_tolerance': 'moderate',
            'benchmark_symbol': '^GSPC'
        })
    
    return jsonify({
        'target_stocks_percent': goals.target_stocks_percent,
        'target_bonds_percent': goals.target_bonds_percent,
        'target_cash_percent': goals.target_cash_percent,
        'target_crypto_percent': goals.target_crypto_percent,
        'target_commodities_percent': goals.target_commodities_percent,
        'risk_tolerance': goals.risk_tolerance,
        'benchmark_symbol': goals.benchmark_symbol
    })


@portfolio_bp.route('/goals', methods=['POST', 'PUT'])
@auth_required
def update_portfolio_goals():
    """Create or update user's investment goals"""
    data = request.get_json()
    
    goals = UserInvestmentGoal.query.filter_by(user_id=request.user.id).first()
    
    if not goals:
        goals = UserInvestmentGoal(user_id=request.user.id)
        db.session.add(goals)
    
    # Update fields
    goals.target_stocks_percent = data.get('target_stocks_percent', goals.target_stocks_percent)
    goals.target_bonds_percent = data.get('target_bonds_percent', goals.target_bonds_percent)
    goals.target_cash_percent = data.get('target_cash_percent', goals.target_cash_percent)
    goals.target_crypto_percent = data.get('target_crypto_percent', goals.target_crypto_percent)
    goals.target_commodities_percent = data.get('target_commodities_percent', goals.target_commodities_percent)
    goals.risk_tolerance = data.get('risk_tolerance', goals.risk_tolerance)
    goals.benchmark_symbol = data.get('benchmark_symbol', goals.benchmark_symbol)
    goals.age = data.get('age', goals.age)
    
    # Validation: Ensure total is 100%
    total = (goals.target_stocks_percent + goals.target_bonds_percent + 
             goals.target_cash_percent + goals.target_crypto_percent + 
             goals.target_commodities_percent)
    
    if total != 100:
        return jsonify({'error': f'Total allocation must be 100%. Current total: {total}%'}), 400
        
    db.session.commit()
    
    return jsonify({'message': 'Investment goals updated successfully'})


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
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

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
    """Add holding to portfolio - creates both holding and transaction record"""
    from models import PortfolioTransaction
    from datetime import date
    
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
    
    # Check if holding already exists
    existing_holding = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id, symbol=symbol).first()
    
    if existing_holding:
        # Update existing holding (add to position)
        old_total = float(existing_holding.shares) * float(existing_holding.avg_buy_price or 0)
        new_total = shares * avg_buy_price
        new_shares = float(existing_holding.shares) + shares
        existing_holding.avg_buy_price = (old_total + new_total) / new_shares if new_shares > 0 else 0
        existing_holding.shares = new_shares
        existing_holding.current_price = current_price
        existing_holding.current_value = new_shares * current_price
        existing_holding.gain_loss = existing_holding.current_value - (new_shares * float(existing_holding.avg_buy_price))
        holding = existing_holding
    else:
        # Create new holding
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
            gain_loss_percent=gain_percent,
            first_buy_date=date.today()
        )
        db.session.add(holding)
    
    # Always create a transaction record for audit trail
    transaction = PortfolioTransaction(
        id=str(uuid.uuid4()),
        portfolio_id=portfolio_id,
        symbol=symbol,
        transaction_type='buy',
        shares=shares,
        price_per_share=avg_buy_price,
        total_amount=shares * avg_buy_price,
        fees=0,
        notes='Initial buy via Add Holding',
        transaction_date=date.today()
    )
    db.session.add(transaction)
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
        'holding': _holding_to_dict(holding),
        'transaction_id': transaction.id
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


@portfolio_bp.route('/<portfolio_id>/transactions', methods=['GET'])
@auth_required
def get_transactions(portfolio_id):
    """Get transaction history for a portfolio"""
    from models import PortfolioTransaction
    
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    # Get filters
    symbol = request.args.get('symbol')
    tx_type = request.args.get('type')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    query = PortfolioTransaction.query.filter_by(portfolio_id=portfolio_id)
    
    if symbol:
        query = query.filter(PortfolioTransaction.symbol == symbol.upper())
    if tx_type:
        query = query.filter(PortfolioTransaction.transaction_type == tx_type)
    
    transactions = query.order_by(desc(PortfolioTransaction.transaction_date)).limit(limit).all()
    
    return jsonify([{
        'id': t.id,
        'symbol': t.symbol,
        'type': t.transaction_type,
        'shares': float(t.shares) if t.shares else 0,
        'pricePerShare': float(t.price_per_share) if t.price_per_share else 0,
        'totalAmount': float(t.total_amount) if t.total_amount else 0,
        'fees': float(t.fees) if t.fees else 0,
        'notes': t.notes,
        'date': t.transaction_date.isoformat() if t.transaction_date else None,
        'createdAt': t.created_at.isoformat() if t.created_at else None
    } for t in transactions])


@portfolio_bp.route('/<portfolio_id>/transactions', methods=['POST'])
@auth_required
def add_transaction(portfolio_id):
    """Add a transaction and update holdings"""
    from models import PortfolioTransaction
    from datetime import date
    
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    data = request.get_json()
    symbol = data.get('symbol', '').upper()
    tx_type = data.get('type', 'buy')  # buy, sell, dividend, split
    shares = float(data.get('shares', 0))
    price = float(data.get('price', 0))
    fees = float(data.get('fees', 0))
    notes = data.get('notes', '')
    tx_date = data.get('date', date.today().isoformat())
    
    if not symbol or shares <= 0:
        return jsonify({'error': 'Symbol and shares required'}), 400
    
    # Create transaction
    transaction = PortfolioTransaction(
        id=str(uuid.uuid4()),
        portfolio_id=portfolio_id,
        symbol=symbol,
        transaction_type=tx_type,
        shares=shares,
        price_per_share=price,
        total_amount=shares * price,
        fees=fees,
        notes=notes,
        transaction_date=tx_date
    )
    db.session.add(transaction)
    
    # Update holding based on transaction type
    holding = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id, symbol=symbol).first()
    
    if tx_type == 'buy':
        if holding:
            # Update average price
            old_total = float(holding.shares) * float(holding.avg_buy_price or 0)
            new_total = shares * price
            new_shares = float(holding.shares) + shares
            holding.avg_buy_price = (old_total + new_total) / new_shares if new_shares > 0 else 0
            holding.shares = new_shares
        else:
            # Create new holding
            holding = PortfolioHolding(
                id=str(uuid.uuid4()),
                portfolio_id=portfolio_id,
                symbol=symbol,
                shares=shares,
                avg_buy_price=price
            )
            db.session.add(holding)
    
    elif tx_type == 'sell':
        if holding and float(holding.shares) >= shares:
            holding.shares = float(holding.shares) - shares
            if float(holding.shares) <= 0:
                db.session.delete(holding)
        else:
            return jsonify({'error': 'Insufficient shares'}), 400
    
    # Update current price from market data
    market = MarketData.query.filter_by(symbol=symbol).first()
    if market and holding and tx_type != 'sell':
        holding.current_price = market.price
        holding.current_value = float(holding.shares) * float(market.price or 0)
        holding.gain_loss = holding.current_value - (float(holding.shares) * float(holding.avg_buy_price or 0))
    
    db.session.commit()
    
    return jsonify({
        'id': transaction.id,
        'message': f'{tx_type.capitalize()} transaction recorded',
        'transaction': {
            'id': transaction.id,
            'symbol': symbol,
            'type': tx_type,
            'shares': shares,
            'price': price
        }
    }), 201


@portfolio_bp.route('/<portfolio_id>/holdings/<holding_id>', methods=['GET'])
@auth_required
def get_holding_detail(portfolio_id, holding_id):
    """Get detailed holding info with transactions"""
    from models import PortfolioTransaction
    
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    holding = PortfolioHolding.query.filter_by(id=holding_id, portfolio_id=portfolio_id).first()
    if not holding:
        return jsonify({'error': 'Holding not found'}), 404
    
    # Get transactions for this symbol
    transactions = PortfolioTransaction.query.filter_by(
        portfolio_id=portfolio_id, 
        symbol=holding.symbol
    ).order_by(desc(PortfolioTransaction.transaction_date)).limit(20).all()
    
    # Get market data for additional info
    market = MarketData.query.filter_by(symbol=holding.symbol).first()
    
    # Calculate metrics
    shares = float(holding.shares or 0)
    avg_cost = float(holding.avg_buy_price or 0)
    current_price = float(market.price if market else holding.current_price or 0)
    total_value = shares * current_price
    total_cost = shares * avg_cost
    total_gain = total_value - total_cost
    gain_percent = (total_gain / total_cost * 100) if total_cost > 0 else 0
    
    # Portfolio weight
    all_holdings = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id).all()
    portfolio_value = sum(float(h.shares or 0) * float(h.current_price or 0) for h in all_holdings)
    weight = (total_value / portfolio_value * 100) if portfolio_value > 0 else 0
    
    return jsonify({
        'holding': {
            'id': holding.id,
            'symbol': holding.symbol,
            'shares': shares,
            'avgCost': avg_cost,
            'currentPrice': current_price,
            'totalValue': round(total_value, 2),
            'totalCost': round(total_cost, 2),
            'totalGain': round(total_gain, 2),
            'gainPercent': round(gain_percent, 2),
            'portfolioWeight': round(weight, 2),
            'firstBuyDate': holding.first_buy_date.isoformat() if holding.first_buy_date else None
        },
        'market': {
            'name': market.name if market else holding.symbol,
            'sector': market.sector if market else None,
            'industry': market.industry if market else None,
            'dayChange': float(market.change) if market and market.change else 0,
            'dayChangePercent': float(market.change_percent) if market and market.change_percent else 0,
            'high52w': float(market._52_week_high) if market and market._52_week_high else None,
            'low52w': float(market._52_week_low) if market and market._52_week_low else None,
            'peRatio': float(market.pe_ratio) if market and market.pe_ratio else None,
            'marketCap': int(market.market_cap) if market and market.market_cap else None
        } if market else None,
        'transactions': [{
            'id': t.id,
            'type': t.transaction_type,
            'shares': float(t.shares),
            'price': float(t.price_per_share) if t.price_per_share else 0,
            'total': float(t.total_amount) if t.total_amount else 0,
            'date': t.transaction_date.isoformat() if t.transaction_date else None
        } for t in transactions]
    })


@portfolio_bp.route('/wealth-history', methods=['GET'])
@auth_required
def get_wealth_history():
    """Get user's wealth history for net worth chart"""
    from models import WealthState
    
    days = min(int(request.args.get('days', 30)), 365)
    
    history = WealthState.query.filter_by(user_id=request.user.id)\
        .order_by(desc(WealthState.date))\
        .limit(days).all()
    
    return jsonify([{
        'date': h.date.isoformat() if h.date else None,
        'totalValue': float(h.total_portfolio_value) if h.total_portfolio_value else 0,
        'totalCash': float(h.total_cash) if h.total_cash else 0,
        'totalInvestments': float(h.total_investments) if h.total_investments else 0,
        'dailyChange': float(h.daily_change) if h.daily_change else 0
    } for h in reversed(history)])


@portfolio_bp.route('/<portfolio_id>/analytics', methods=['GET'])
@auth_required
def get_portfolio_analytics(portfolio_id):
    """Get portfolio analytics: allocation, performance, risk"""
    portfolio = UserPortfolio.query.filter_by(id=portfolio_id, user_id=request.user.id).first()
    if not portfolio:
        return jsonify({'error': 'Portfolio not found'}), 404
    
    holdings = PortfolioHolding.query.filter_by(portfolio_id=portfolio_id).all()
    
    if not holdings:
        return jsonify({
            'totalValue': 0,
            'totalGain': 0,
            'allocation': [],
            'sectorBreakdown': [],
            'topPerformers': [],
            'worstPerformers': []
        })
    
    # Calculate allocations
    allocation = []
    sector_map = {}
    total_value = 0
    total_gain = 0
    
    for h in holdings:
        market = MarketData.query.filter_by(symbol=h.symbol).first()
        shares = float(h.shares or 0)
        current_price = float(market.price if market else h.current_price or 0)
        avg_cost = float(h.avg_buy_price or 0)
        value = shares * current_price
        cost = shares * avg_cost
        gain = value - cost
        gain_percent = (gain / cost * 100) if cost > 0 else 0
        
        total_value += value
        total_gain += gain
        
        allocation.append({
            'symbol': h.symbol,
            'name': market.name if market else h.symbol,
            'value': round(value, 2),
            'gain': round(gain, 2),
            'gainPercent': round(gain_percent, 2),
            'shares': shares,
            'sector': market.sector if market else 'Unknown'
        })
        
        # Sector aggregation
        sector = market.sector if market else 'Unknown'
        if sector not in sector_map:
            sector_map[sector] = 0
        sector_map[sector] += value
    
    # Calculate percentages
    for item in allocation:
        item['weight'] = round((item['value'] / total_value * 100) if total_value > 0 else 0, 2)
    
    # Sort for top/worst performers
    sorted_by_gain = sorted(allocation, key=lambda x: x['gainPercent'], reverse=True)
    
    return jsonify({
        'totalValue': round(total_value, 2),
        'totalGain': round(total_gain, 2),
        'totalGainPercent': round((total_gain / (total_value - total_gain) * 100) if (total_value - total_gain) > 0 else 0, 2),
        'holdingsCount': len(holdings),
        'allocation': sorted(allocation, key=lambda x: x['value'], reverse=True),
        'sectorBreakdown': [
            {'sector': k, 'value': round(v, 2), 'weight': round((v / total_value * 100) if total_value > 0 else 0, 2)}
            for k, v in sorted(sector_map.items(), key=lambda x: x[1], reverse=True)
        ],
        'topPerformers': sorted_by_gain[:5],
        'worstPerformers': sorted_by_gain[-5:][::-1] if len(sorted_by_gain) >= 5 else sorted_by_gain[::-1]
    })
