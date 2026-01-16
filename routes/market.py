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

market_bp = Blueprint('market', __name__)


@market_bp.route('/overview', methods=['GET'])
def get_market_overview():
    """Get comprehensive market overview data"""
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
        md_filter
    ).order_by(desc(MarketData.change_percent)).limit(5).all()

    # Get top losers (scoped)
    losers = MarketData.query.filter(
        MarketData.change_percent < 0,
        MarketData.asset_type == 'stock',
        md_filter
    ).order_by(asc(MarketData.change_percent)).limit(5).all()

    # Get most active (scoped)
    most_active = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.volume != None,
        md_filter
    ).order_by(desc(MarketData.volume)).limit(5).all()
    
    # Calculate market stats
    all_stocks = MarketData.query.filter(MarketData.asset_type == 'stock').all()
    advancers = sum(1 for s in all_stocks if s.change_percent and s.change_percent > 0)
    decliners = sum(1 for s in all_stocks if s.change_percent and s.change_percent < 0)
    unchanged = len(all_stocks) - advancers - decliners
    total_volume = sum(s.volume or 0 for s in all_stocks)
    
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
        md_filter = (MarketData.country_code == 'US')
    else:
        hc = header_country.strip().upper()
        md_filter = (MarketData.country_code == 'GLOBAL') if hc == 'GLOBAL' else (MarketData.country_code == hc)

    query = MarketData.query.filter(MarketData.asset_type == 'stock', md_filter)
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

