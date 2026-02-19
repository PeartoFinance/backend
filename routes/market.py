"""
Market API Routes
Endpoints for market data, indices, commodities, and stock offers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from models import (
    db, MarketData, MarketIndices, CommodityData, StockOffer,
    Dividend, BulkTransaction, ForexRate
)
from handlers.market_data.calendar_handler import get_economic_events
from handlers.market_data.forex_handler import get_forex_history
from extensions import cache
from utils.validators import safe_int

market_bp = Blueprint('market', __name__)


@market_bp.route('/forex/history/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_forex_pair_history(symbol):
    """Get historical data for a forex pair"""
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    return jsonify(get_forex_history(symbol, period, interval))


@market_bp.route('/calendar', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_calendar():
    """Get economic calendar events"""
    start = request.args.get('start')
    end = request.args.get('end')
    # Safe conversion: Returns 50 if user sends invalid characters
    limit = min(safe_int(request.args.get('limit'), 50), 100)
    
    events = get_economic_events(start, end, limit)
    return jsonify(events)


@market_bp.route('/overview', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_market_overview():
    """Get comprehensive market overview data - cached for 5 minutes"""
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
        idx_filter = MarketIndices.country_code.in_([hc, 'GLOBAL'])
    else:
        # UX IMPROVEMENT: Fallback to 'US' instead of just 'GLOBAL' if header is missing.
        # This prevents the "Empty Dashboard" bug for guest users.
        md_filter = MarketData.country_code.in_(['US', 'GLOBAL'])
        idx_filter = MarketIndices.country_code.in_(['US', 'GLOBAL'])

    # Get indices (scoped)
    indices = MarketIndices.query.filter(idx_filter).limit(6).all()

    # Get top gainers (scoped)
    gainers = MarketData.query.filter(
        MarketData.change_percent > 0,
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        md_filter
    ).order_by(desc(MarketData.change_percent)).limit(5).all()

    # Get top losers (scoped)
    losers = MarketData.query.filter(
        MarketData.change_percent < 0,
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        md_filter
    ).order_by(asc(MarketData.change_percent)).limit(5).all()

    # Get most active (scoped)
    most_active = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
        MarketData.volume != None,
        md_filter
    ).order_by(desc(MarketData.volume)).limit(5).all()
    
    # Calculate market stats using efficient SQL COUNT with the SAME country filter
    advancers = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent > 0,
        md_filter
    ).scalar() or 0
    
    decliners = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent < 0,
        md_filter
    ).scalar() or 0
    
    total_count = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        md_filter
    ).scalar() or 0
    unchanged = total_count - advancers - decliners
    
    total_volume = db.session.query(db.func.sum(MarketData.volume)).filter(
        MarketData.asset_type == 'stock',
        md_filter
    ).scalar() or 0
    
    return jsonify({
        'indices': [idx.to_dict() for idx in indices],
        'topGainers': [g.to_dict() for g in gainers],
        'topLosers': [l.to_dict() for l in losers],
        'mostActive': [{
            'symbol': s.symbol,
            'name': s.name,
            'price': float(s.price) if s.price else None,
            'change': float(s.change) if s.change else None,
            'changePercent': float(s.change_percent) if s.change_percent else None,
            'volume': s.volume
        } for s in most_active],
        'advancers': advancers,
        'decliners': decliners,
        'unchanged': unchanged,
        'totalVolume': total_volume
    })


@market_bp.route('/indices', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_indices():
    """Get all market indices - cached for 5 minutes"""""
    region = request.args.get('region')

    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        idx_filter = MarketIndices.country_code.in_([hc, 'GLOBAL'])
    else:
        # UX IMPROVEMENT: Fallback to 'US' instead of just 'GLOBAL' if header is missing.
        idx_filter = MarketIndices.country_code.in_(['US', 'GLOBAL'])

    query = MarketIndices.query.filter(idx_filter)
    if region:
        query = query.filter(MarketIndices.region == region)

    indices = query.all()
    return jsonify([idx.to_dict() for idx in indices])


@market_bp.route('/forex', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_forex_metrics():
    """Get all forex rates - cached for 5 minutes"""""
    rates = ForexRate.query.all()
    # If no rates found, return empty list instead of 404
    return jsonify([r.to_dict() for r in rates])


@market_bp.route('/commodities', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_commodities():
    """Get commodities data - cached for 5 minutes"""
    # Commodities are global by default; keep as-is but allow header to filter if model had country_code
    header_country = request.headers.get('X-User-Country')
    query = CommodityData.query
    if header_country:
        hc = header_country.strip().upper()
        if hasattr(CommodityData, 'country_code'):
            query = query.filter(CommodityData.country_code.in_([hc, 'GLOBAL']))
    else:
        if hasattr(CommodityData, 'country_code'):
            query = query.filter(CommodityData.country_code == 'GLOBAL')

    commodities = query.all()
    return jsonify([c.to_dict() for c in commodities])


@market_bp.route('/offers', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_offers():
    """Get stock offers (IPO, FPO)"""
    status = request.args.get('status')
    offer_type = request.args.get('type')
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        offer_filter = StockOffer.country_code.in_([hc, 'GLOBAL'])
    else:
        offer_filter = (StockOffer.country_code == 'GLOBAL')

    query = StockOffer.query
    if status:
        query = query.filter(StockOffer.status == status)
    if offer_type:
        query = query.filter(StockOffer.offer_type == offer_type)
    if offer_filter is not None:
        query = query.filter(offer_filter)

    offers = query.order_by(desc(StockOffer.created_at)).all()
    
    return jsonify([{
        'id': o.id,
        'symbol': o.symbol,
        'companyName': o.company_name,
        'offerType': o.offer_type,
        'priceRange': o.price_range,
        'openDate': o.open_date.isoformat() if o.open_date else None,
        'closeDate': o.close_date.isoformat() if o.close_date else None,
        'listingDate': o.listing_date.isoformat() if o.listing_date else None,
        'status': o.status
    } for o in offers])


@market_bp.route('/stocks', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_all_stocks():
    """Get all stocks with optional filters"""
    sector = request.args.get('sector')
    # Safe conversion: Prevents crash if limit is not a number
    limit = min(safe_int(request.args.get('limit'), 50), 100)
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        # UX IMPROVEMENT: Fallback to 'US' instead of just 'GLOBAL' if header is missing.
        md_filter = MarketData.country_code.in_(['US', 'GLOBAL'])
    else:
        hc = header_country.strip().upper()
        md_filter = (MarketData.country_code == 'GLOBAL') if hc == 'GLOBAL' else (MarketData.country_code == hc)

    query = MarketData.query.filter(
        MarketData.asset_type == 'stock', 
        MarketData.is_listed == True,
        md_filter
    )
    if sector:
        query = query.filter(MarketData.sector == sector)

    stocks = query.limit(limit).all()
    return jsonify([s.to_dict() for s in stocks])


@market_bp.route('/crypto', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_crypto_markets():
    """Alias for crypto markets under /api/market/crypto."""
    # Safe conversion: Returns 100 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 100), 250)
    # Safe conversion: Returns page 1 if invalid characters sent
    page = max(safe_int(request.args.get('page'), 1), 1)
    sort_by = request.args.get('sort', 'market_cap')

    offset = (page - 1) * limit

    sort_map = {
        'market_cap': MarketData.market_cap,
        'price': MarketData.price,
        'change': MarketData.change_percent,
        'volume': MarketData.volume,
    }
    sort_column = sort_map.get(sort_by, MarketData.market_cap)

    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        # UX IMPROVEMENT: Fallback to 'US' instead of just 'GLOBAL' if header is missing.
        md_filter = MarketData.country_code.in_(['US', 'GLOBAL'])

    cryptos = MarketData.query.filter(
        MarketData.asset_type == 'crypto',
        md_filter
    ).order_by(desc(sort_column)).offset(offset).limit(limit).all()

    return jsonify([c.to_dict() for c in cryptos])


@market_bp.route('/stats', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_market_stats():
    """
    High-level market breadth stats for /api/market/stats.
    PERFORMANCE FIX: Use database aggregation (COUNT/SUM) instead of fetching 
    all records into memory. This prevents server crashes as the database grows.
    """
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        # Fallback to US/GLOBAL for guest users
        md_filter = MarketData.country_code.in_(['US', 'GLOBAL'])

    # Query counts directly from the database (much faster and memory-efficient)
    advancers = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent > 0,
        md_filter
    ).scalar() or 0
    
    decliners = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent < 0,
        md_filter
    ).scalar() or 0
    
    total_count = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        md_filter
    ).scalar() or 0
    
    total_volume = db.session.query(db.func.sum(MarketData.volume)).filter(
        MarketData.asset_type == 'stock',
        md_filter
    ).scalar() or 0
    
    unchanged = total_count - advancers - decliners

    return jsonify({
        'advancers': advancers,
        'decliners': decliners,
        'unchanged': unchanged,
        'totalVolume': total_volume,
        'totalCount': total_count,
    })


@market_bp.route('/dividends', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_dividends():
    """Get proposed dividends from database."""
    status = request.args.get('status')  # 'proposed', 'approved', 'paid'
    # Safe conversion: Returns 50 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 50), 100)
    header_country = request.headers.get('X-User-Country')
    query = Dividend.query
    if status:
        query = query.filter(Dividend.status == status)
    if header_country and hasattr(Dividend, 'country_code'):
        hc = header_country.strip().upper()
        query = query.filter(Dividend.country_code.in_([hc, 'GLOBAL']))
    elif hasattr(Dividend, 'country_code'):
        query = query.filter(Dividend.country_code == 'GLOBAL')

    dividends = query.order_by(desc(Dividend.created_at)).limit(limit).all()
    return jsonify([d.to_dict() for d in dividends])


@market_bp.route('/bulk-transactions', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_bulk_transactions():
    """Get bulk transactions from database."""
    limit = min(int(request.args.get('limit', 50)), 100)
    symbol = request.args.get('symbol')
    header_country = request.headers.get('X-User-Country')
    query = BulkTransaction.query
    if symbol:
        query = query.filter(BulkTransaction.symbol == symbol.upper())
    if header_country and hasattr(BulkTransaction, 'country_code'):
        hc = header_country.strip().upper()
        query = query.filter(BulkTransaction.country_code.in_([hc, 'GLOBAL']))
    elif hasattr(BulkTransaction, 'country_code'):
        query = query.filter(BulkTransaction.country_code == 'GLOBAL')

    transactions = query.order_by(desc(BulkTransaction.transaction_date)).limit(limit).all()
    return jsonify([t.to_dict() for t in transactions])


@market_bp.route('/sector-analysis', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_sector_analysis():
    """
    Get comprehensive sector analysis for market visualization.
    PERFORMANCE FIX: Use SQL GROUP BY instead of fetching 5000+ records into memory.
    """
    from sqlalchemy import func
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        # Fallback to US/GLOBAL for guest users
        md_filter = MarketData.country_code.in_(['US', 'GLOBAL'])   

    # Aggregate data by sector directly in SQL (Massive performance boost)
    sector_stats = db.session.query(
        MarketData.sector,
        func.sum(MarketData.volume * MarketData.price).label('turnover'),
        func.sum(MarketData.volume).label('volume'),
        func.count(MarketData.id).label('stock_count'),
        func.avg(MarketData.change_percent).label('avg_change'),
        func.avg(MarketData.ytd_return).label('avg_ytd'),
        func.sum(db.case((MarketData.change_percent > 0, 1), else_=0)).label('advancers'),
        func.sum(db.case((MarketData.change_percent < 0, 1), else_=0)).label('decliners'),
        func.sum(db.case((MarketData.change_percent == 0, 1), else_=0)).label('unchanged')
    ).filter(
        MarketData.asset_type == 'stock',
        MarketData.sector.isnot(None),
        MarketData.sector != '',
        md_filter
    ).group_by(MarketData.sector).all()

    # Calculate global totals for percentages
    total_turnover = sum(s.turnover or 0 for s in sector_stats)
    total_volume = sum(s.volume or 0 for s in sector_stats)
    total_stocks = sum(s.stock_count or 0 for s in sector_stats)

    sectors = []
    for s in sector_stats:
        sector_name = s.sector or 'Others'
        sectors.append({
            'sector': sector_name,
            'turnover': float(round(s.turnover or 0, 2)),
            'turnoverPercent': float(round((s.turnover / total_turnover * 100) if total_turnover > 0 else 0, 2)),
            'volume': int(s.volume or 0),
            'volumePercent': float(round((s.volume / total_volume * 100) if total_volume > 0 else 0, 2)),
            'stockCount': int(s.stock_count or 0),
            'weight': float(round((s.stock_count / total_stocks * 100) if total_stocks > 0 else 0, 2)),
            'avgChangePercent': float(round(s.avg_change or 0, 2)),
            'avgYtdReturn': float(round(s.avg_ytd or 0, 2)),
            'advancers': int(s.advancers or 0),
            'decliners': int(s.decliners or 0),
            'unchanged': int(s.unchanged or 0)
        })

    # Sort by turnover descending
    sectors.sort(key=lambda x: x['turnover'], reverse=True)

    return jsonify({
        'sectors': sectors,
        'totals': {
            'turnover': float(round(total_turnover, 2)),
            'volume': int(total_volume),
            'transactions': int(total_stocks),
            'sectorCount': len(sectors)
        }
    })



@market_bp.route('/technical-analysis/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_technical_analysis_route(symbol):
    """
    Get technical analysis summary and indicators for a symbol.
    """
    try:
        from services.technical_analysis import analyze_stock
        from handlers.market_data.stock_handler import get_stock_history
        
        # Fetch 6 months of daily data to ensure enough points for MA200
        history = get_stock_history(symbol, period='6mo', interval='1d')
        
        # get_stock_history returns a list of dicts: {'date': ..., 'close': ...}
        if not history:
             return jsonify({
                'symbol': symbol, 
                'status': 'error', 
                'message': 'No historical data available'
            }), 404
            
        analysis = analyze_stock(symbol, history)
        return jsonify(analysis)
        
    except Exception as e:
         return jsonify({'error': str(e)}), 500
