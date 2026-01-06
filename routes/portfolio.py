"""
Portfolio API Routes
Endpoints for user watchlists and portfolios
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc
from models import db, Watchlist, WatchlistItem, UserPortfolio, PortfolioHolding, MarketData

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/watchlist', methods=['GET'])
def get_watchlist():
    """Get user's default watchlist items"""
    # For demo, return sample data with real market prices
    watchlist_symbols = ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN']
    
    stocks = MarketData.query.filter(MarketData.symbol.in_(watchlist_symbols)).all()
    
    return jsonify([{
        'id': i + 1,
        'symbol': s.symbol,
        'name': s.name,
        'price': float(s.price) if s.price else 0,
        'change': float(s.change) if s.change else 0,
        'changePercent': float(s.change_percent) if s.change_percent else 0,
        'addedAt': s.last_updated.isoformat() if s.last_updated else None
    } for i, s in enumerate(stocks)])


@portfolio_bp.route('/watchlist', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    data = request.get_json()
    symbol = data.get('symbol')
    
    if not symbol:
        return jsonify({'error': 'Symbol required'}), 400
    
    # In production, would save to user's watchlist
    return jsonify({'message': f'{symbol} added to watchlist'})


@portfolio_bp.route('/watchlist/<symbol>', methods=['DELETE'])
def remove_from_watchlist(symbol):
    """Remove stock from watchlist"""
    return jsonify({'message': f'{symbol} removed from watchlist'})


@portfolio_bp.route('/watchlists', methods=['GET'])
def get_watchlists():
    """Get all user watchlists"""
    watchlists = Watchlist.query.limit(10).all()
    
    return jsonify([{
        'id': w.id,
        'name': w.name,
        'items': [],
        'createdAt': w.created_at.isoformat() if w.created_at else None
    } for w in watchlists])


@portfolio_bp.route('/list', methods=['GET'])
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
def create_portfolio():
    """Create new portfolio"""
    data = request.get_json()
    name = data.get('name', 'My Portfolio')
    
    return jsonify({
        'id': 1,
        'name': name,
        'totalValue': 0,
        'holdings': []
    })
