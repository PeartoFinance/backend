"""
Market API Routes
Endpoints for market data, indices, commodities, and stock offers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from models import (
    db, MarketData, MarketIndices, CommodityData, StockOffer,
    Dividend, BulkTransaction
)
from handlers.market_data.calendar_handler import get_economic_events
from handlers.market_data.forex_handler import get_forex_history
from extensions import cache

market_bp = Blueprint('market', __name__)


@market_bp.route('/forex/history/<symbol>', methods=['GET'])
def get_forex_pair_history(symbol):
    """Get historical data for a forex pair"""
    period = request.args.get('period', '1mo')
    interval = request.args.get('interval', '1d')
    return jsonify(get_forex_history(symbol, period, interval))


@market_bp.route('/calendar', methods=['GET'])
def get_calendar():
    """Get economic calendar events"""
    start = request.args.get('start')
    end = request.args.get('end')
    limit = min(int(request.args.get('limit', 50)), 100)
    
    events = get_economic_events(start, end, limit)
    return jsonify(events)


@market_bp.route('/overview', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
def get_market_overview():
    """Get comprehensive market overview data - cached for 30s"""
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
        idx_filter = MarketIndices.country_code.in_([hc, 'GLOBAL'])
    else:
        # default to GLOBAL-only
        md_filter = (MarketData.country_code == 'GLOBAL')
        idx_filter = (MarketIndices.country_code == 'GLOBAL')

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
    
    # Calculate market stats using efficient SQL COUNT (instead of loading all rows)
    advancers = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent > 0
    ).scalar() or 0
    
    decliners = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock',
        MarketData.change_percent < 0
    ).scalar() or 0
    
    total_count = db.session.query(db.func.count(MarketData.id)).filter(
        MarketData.asset_type == 'stock'
    ).scalar() or 0
    unchanged = total_count - advancers - decliners
    
    total_volume = db.session.query(db.func.sum(MarketData.volume)).filter(
        MarketData.asset_type == 'stock'
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
def get_indices():
    """Get all market indices"""
    region = request.args.get('region')

    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        idx_filter = MarketIndices.country_code.in_([hc, 'GLOBAL'])
    else:
        idx_filter = (MarketIndices.country_code == 'GLOBAL')

    query = MarketIndices.query.filter(idx_filter)
    if region:
        query = query.filter(MarketIndices.region == region)

    indices = query.all()
    return jsonify([idx.to_dict() for idx in indices])


@market_bp.route('/commodities', methods=['GET'])
def get_commodities():
    """Get commodities data"""
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
def get_all_stocks():
    """Get all stocks with optional filters"""
    sector = request.args.get('sector')
    limit = min(int(request.args.get('limit', 50)), 100)
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        # Default to GLOBAL/All similar to crypto if no country specified
        md_filter = (MarketData.country_code == 'GLOBAL')
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
def get_crypto_markets():
    """Alias for crypto markets under /api/market/crypto."""
    limit = min(int(request.args.get('limit', 100)), 250)
    page = max(int(request.args.get('page', 1)), 1)
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
        md_filter = (MarketData.country_code == 'GLOBAL')

    cryptos = MarketData.query.filter(
        MarketData.asset_type == 'crypto',
        md_filter
    ).order_by(desc(sort_column)).offset(offset).limit(limit).all()

    return jsonify([c.to_dict() for c in cryptos])


@market_bp.route('/stats', methods=['GET'])
def get_market_stats():
    """High-level market breadth stats for /api/market/stats."""
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        md_filter = (MarketData.country_code == 'GLOBAL')

    all_stocks = MarketData.query.filter(MarketData.asset_type == 'stock', md_filter).all()

    advancers = sum(1 for s in all_stocks if s.change_percent and s.change_percent > 0)
    decliners = sum(1 for s in all_stocks if s.change_percent and s.change_percent < 0)
    unchanged = len(all_stocks) - advancers - decliners
    total_volume = sum(s.volume or 0 for s in all_stocks)

    return jsonify({
        'advancers': advancers,
        'decliners': decliners,
        'unchanged': unchanged,
        'totalVolume': total_volume,
        'totalCount': len(all_stocks),
    })


@market_bp.route('/dividends', methods=['GET'])
def get_dividends():
    """Get proposed dividends from database."""
    status = request.args.get('status')  # 'proposed', 'approved', 'paid'
    limit = min(int(request.args.get('limit', 50)), 100)
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
    Returns sector breakdown by turnover, volume, and transaction count.
    """
    from sqlalchemy import func
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        hc = header_country.strip().upper()
        md_filter = MarketData.country_code.in_([hc, 'GLOBAL'])
    else:
        md_filter = (MarketData.country_code == 'GLOBAL')

    # Get all stocks grouped by sector
    stocks = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.sector.isnot(None),
        MarketData.sector != '',
        md_filter
    ).all()

    # Aggregate by sector
    sector_data = {}
    for stock in stocks:
        sector = stock.sector or 'Others'
        if sector not in sector_data:
            sector_data[sector] = {
                'sector': sector,
                'turnover': 0,
                'volume': 0,
                'transactions': 0,  # count of stocks as proxy
                'totalChange': 0,
                'changeCount': 0,
                'totalYTD': 0,
                'ytdCount': 0,
                'advancers': 0,
                'decliners': 0,
                'unchanged': 0
            }
        
        # Calculate turnover (volume * price)
        turnover = (stock.volume or 0) * (stock.price or 0)
        sector_data[sector]['turnover'] += turnover
        sector_data[sector]['volume'] += stock.volume or 0
        sector_data[sector]['transactions'] += 1
        
        if stock.change_percent:
            sector_data[sector]['totalChange'] += stock.change_percent
            sector_data[sector]['changeCount'] += 1
            
            if stock.change_percent > 0:
                sector_data[sector]['advancers'] += 1
            elif stock.change_percent < 0:
                sector_data[sector]['decliners'] += 1
            else:
                sector_data[sector]['unchanged'] += 1
        else:
            sector_data[sector]['unchanged'] += 1
            
        # PROD ADDITION: Accumulate YTD for average calculation
        if stock.ytd_return is not None:
            sector_data[sector]['totalYTD'] += stock.ytd_return
            sector_data[sector]['ytdCount'] += 1

    # Calculate totals for percentages
    total_turnover = sum(s['turnover'] for s in sector_data.values())
    total_volume = sum(s['volume'] for s in sector_data.values())
    total_transactions = sum(s['transactions'] for s in sector_data.values())

    # Build response with percentages
    sectors = []
    for sector, data in sector_data.items():
        avg_change = float(data['totalChange']) / float(data['changeCount']) if data['changeCount'] > 0 else 0.0
        avg_ytd = float(data['totalYTD']) / float(data['ytdCount']) if data['ytdCount'] > 0 else 0.0
        
        sectors.append({
            'sector': sector,
            'turnover': float(round(data['turnover'], 2)),
            'turnoverPercent': float(round((data['turnover'] / total_turnover * 100) if total_turnover > 0 else 0, 2)),
            'volume': int(data['volume']),
            'volumePercent': float(round((data['volume'] / total_volume * 100) if total_volume > 0 else 0, 2)),
            'stockCount': int(data['transactions']),
            'weight': float(round((data['transactions'] / total_transactions * 100) if total_transactions > 0 else 0, 2)),
            'avgChangePercent': float(round(avg_change, 2)),
            'avgYtdReturn': float(round(avg_ytd, 2)),
            'advancers': int(data['advancers']),
            'decliners': int(data['decliners']),
            'unchanged': int(data['unchanged'])
        })

    # Sort by turnover descending
    sectors.sort(key=lambda x: x['turnover'], reverse=True)

    return jsonify({
        'sectors': sectors,
        'totals': {
            'turnover': round(total_turnover, 2),
            'volume': total_volume,
            'transactions': total_transactions,
            'sectorCount': len(sectors)
        }
    })
