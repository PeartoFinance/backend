"""
Market API Routes
Endpoints for market data, indices, commodities, and stock offers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from models import (
    db, MarketData, MarketIndices, CommodityData, StockOffer
)

market_bp = Blueprint('market', __name__)


@market_bp.route('/overview', methods=['GET'])
def get_market_overview():
    """Get comprehensive market overview data"""
    country = getattr(request, 'user_country', 'US')
    
    # Get indices
    indices = MarketIndices.query.limit(6).all()
    
    # Get top gainers
    gainers = MarketData.query.filter(
        MarketData.change_percent > 0,
        MarketData.asset_type == 'stock'
    ).order_by(desc(MarketData.change_percent)).limit(5).all()
    
    # Get top losers
    losers = MarketData.query.filter(
        MarketData.change_percent < 0,
        MarketData.asset_type == 'stock'
    ).order_by(asc(MarketData.change_percent)).limit(5).all()
    
    # Get most active
    most_active = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.volume != None
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
    
    query = MarketIndices.query
    if region:
        query = query.filter(MarketIndices.region == region)
    
    indices = query.all()
    return jsonify([idx.to_dict() for idx in indices])


@market_bp.route('/commodities', methods=['GET'])
def get_commodities():
    """Get commodities data"""
    commodities = CommodityData.query.all()
    return jsonify([c.to_dict() for c in commodities])


@market_bp.route('/offers', methods=['GET'])
def get_stock_offers():
    """Get stock offers (IPO, FPO)"""
    status = request.args.get('status')
    offer_type = request.args.get('type')
    
    query = StockOffer.query
    if status:
        query = query.filter(StockOffer.status == status)
    if offer_type:
        query = query.filter(StockOffer.offer_type == offer_type)
    
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
    
    query = MarketData.query.filter(MarketData.asset_type == 'stock')
    if sector:
        query = query.filter(MarketData.sector == sector)
    
    stocks = query.limit(limit).all()
    return jsonify([s.to_dict() for s in stocks])
