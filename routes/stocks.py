"""
Stocks API Routes with SQLAlchemy
- Quotes, search, profile, history, movers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from models.base import db
from models.market import MarketData, CompanyFinancials, MarketIssue
from models.article import NewsItem

stocks_bp = Blueprint('stocks', __name__)


@stocks_bp.route('/quotes', methods=['GET'])
def get_quotes():
    """Get real-time quotes for multiple symbols"""
    symbols_param = request.args.get('symbols', '')
    
    if not symbols_param:
        return jsonify({'error': 'symbols parameter required'}), 400
    
    symbols = [s.strip().upper() for s in symbols_param.split(',')]

    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        # no header -> default to GLOBAL only
        filter_condition = (MarketData.country_code == 'GLOBAL')

    prices = MarketData.query.filter(
        MarketData.symbol.in_(symbols),
        MarketData.asset_type == 'stock',
        filter_condition
    ).all()
    
    return jsonify([p.to_dict() for p in prices])


@stocks_bp.route('/search', methods=['GET'])
def search_stocks():
    """Search stocks by name or symbol"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 10)), 50)
    
    if not query:
        return jsonify({'error': 'q parameter required'}), 400
    
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        filter_condition = (MarketData.country_code == 'US')
    else:
        country = header_country.strip().upper()
        filter_condition = (MarketData.country_code == 'GLOBAL') if country == 'GLOBAL' else (MarketData.country_code == country)

    stocks = MarketData.query.filter(
        db.or_(
            MarketData.symbol.ilike(f'%{query}%'),
            MarketData.name.ilike(f'%{query}%')
        ),
        MarketData.asset_type == 'stock',
        filter_condition
    ).limit(limit).all()
    
    return jsonify([s.to_dict() for s in stocks])


@stocks_bp.route('/profile/<symbol>', methods=['GET'])
def get_profile(symbol):
    """Get expanded stock profile including financials, news, and issues"""
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    symbol = symbol.upper()
    stock = MarketData.query.filter(
        MarketData.symbol == symbol,
        MarketData.asset_type == 'stock',
        filter_condition
    ).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    # Get basic data
    data = stock.to_dict()
    
    # 1. Get Financials (Latest 4 records)
    financials = CompanyFinancials.query.filter_by(symbol=symbol).order_by(CompanyFinancials.fiscal_date_ending.desc()).limit(4).all()
    data['financials'] = [f.to_dict() for f in financials]
    
    # 2. Get Market Issues (Active ones)
    issues = MarketIssue.query.filter_by(symbol=symbol, is_active=True).order_by(MarketIssue.issue_date.desc()).all()
    data['marketIssues'] = [i.to_dict() for i in issues]
    
    # 3. Get Related News
    news = NewsItem.query.filter_by(related_symbol=symbol).order_by(NewsItem.published_at.desc()).limit(5).all()
    if not news:
        # Fallback to general news if no symbol-specific news found
        news = NewsItem.query.filter(
            NewsItem.title.ilike(f'%{symbol}%'),
            NewsItem.curated_status == 'published'
        ).order_by(NewsItem.published_at.desc()).limit(5).all()
    
    data['news'] = [n.to_dict() for n in news]
    
    return jsonify(data)


@stocks_bp.route('/directory', methods=['GET'])
def get_business_directory():
    """List all businesses marked as 'is_listed' for the public directory"""
    try:
        from handlers.market_data.business_handler import get_business_directory
        
        search = request.args.get('q', '')
        header_country = request.headers.get('X-User-Country', 'US')
        limit = min(int(request.args.get('limit', 20)), 100)
        
        businesses = get_business_directory(search=search, country=header_country, limit=limit)
        return jsonify(businesses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stocks_bp.route('/movers', methods=['GET'])
def get_movers():
    """Get top gainers and losers"""
    mover_type = request.args.get('type', 'both')
    limit = min(int(request.args.get('limit', 10)), 50)
    
    result = {}
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    if mover_type in ('gainers', 'both'):
        gainers = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent > 0,
            filter_condition
        ).order_by(desc(MarketData.change_percent)).limit(limit).all()
        result['gainers'] = [g.to_dict() for g in gainers]
    
    if mover_type in ('losers', 'both'):
        losers = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.change_percent < 0,
            filter_condition
        ).order_by(asc(MarketData.change_percent)).limit(limit).all()
        result['losers'] = [l.to_dict() for l in losers]
    
    return jsonify(result)


@stocks_bp.route('/most-active', methods=['GET'])
def get_most_active():
    """Get most actively traded stocks"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    stocks = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.volume != None,
        filter_condition
    ).order_by(desc(MarketData.volume)).limit(limit).all()
    
    return jsonify([{
        'symbol': s.symbol,
        'name': s.name,
        'price': float(s.price) if s.price else None,
        'volume': s.volume
    } for s in stocks])


@stocks_bp.route('/etfs', methods=['GET'])
def get_etfs():
    """List all ETFs with optional search and pagination"""
    query = request.args.get('q', '').strip()
    limit = min(int(request.args.get('limit', 20)), 100)
    page = max(int(request.args.get('page', 1)), 1)
    offset = (page - 1) * limit

    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    base_query = MarketData.query.filter(
        MarketData.asset_type == 'etf',
        filter_condition
    )

    if query:
        base_query = base_query.filter(
            db.or_(
                MarketData.symbol.ilike(f'%{query}%'),
                MarketData.name.ilike(f'%{query}%')
            )
        )

    etfs = base_query.order_by(desc(MarketData.market_cap)).offset(offset).limit(limit).all()
    
    return jsonify([e.to_dict() for e in etfs])


@stocks_bp.route('/etfs/movers', methods=['GET'])
def get_etf_movers():
    """Get top ETF gainers and losers"""
    limit = min(int(request.args.get('limit', 10)), 50)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    gainers = MarketData.query.filter(
        MarketData.asset_type == 'etf',
        MarketData.change_percent > 0,
        filter_condition
    ).order_by(desc(MarketData.change_percent)).limit(limit).all()

    losers = MarketData.query.filter(
        MarketData.asset_type == 'etf',
        MarketData.change_percent < 0,
        filter_condition
    ).order_by(asc(MarketData.change_percent)).limit(limit).all()
    
    return jsonify({
        'gainers': [g.to_dict() for g in gainers],
        'losers': [l.to_dict() for l in losers]
    })

@stocks_bp.route('/history/<symbol>', methods=['GET'])
def get_history(symbol):
    """Get price history for a symbol (Stock, ETF, or Crypto)"""
    try:
        from handlers.market_data.stock_handler import get_stock_history
        
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        history = get_stock_history(symbol.upper(), period=period, interval=interval)
        
        if not history:
            return jsonify({'error': 'No history found for this symbol'}), 404
            
        return jsonify({
            'symbol': symbol.upper(),
            'period': period,
            'interval': interval,
            'data': history
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
