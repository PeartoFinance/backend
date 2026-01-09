"""
Admin Market Routes - Market data management
"""
from flask import Blueprint, jsonify, request
from .auth import admin_required
from models import db, MarketData, MarketIndices, MarketSentiment, CryptoMarketData, CommodityData
from datetime import datetime

market_bp = Blueprint('admin_market', __name__)


@market_bp.route('/market-data', methods=['GET'])
@admin_required
def get_market_data():
    """List market data with filters"""
    try:
        asset_type = request.args.get('type', 'stock')
        search = request.args.get('search', '')
        limit = int(request.args.get('limit', 100))
        
        query = MarketData.query.filter(MarketData.asset_type == asset_type)
        if search:
            query = query.filter(
                db.or_(
                    MarketData.symbol.ilike(f'%{search}%'),
                    MarketData.name.ilike(f'%{search}%')
                )
            )
        items = query.order_by(MarketData.symbol).limit(limit).all()
        
        return jsonify({
            'items': [{
                'id': m.id,
                'symbol': m.symbol,
                'name': m.name,
                'price': float(m.price) if m.price else 0,
                'change': float(m.change) if m.change else 0,
                'change_percent': float(m.change_percent) if m.change_percent else 0,
                'volume': m.volume,
                'market_cap': float(m.market_cap) if m.market_cap else 0,
                'asset_type': m.asset_type,
                'last_updated': m.last_updated.isoformat() if m.last_updated else None
            } for m in items],
            'total': len(items)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/stats', methods=['GET'])
@admin_required
def get_market_stats():
    """Get market data statistics"""
    try:
        stocks = MarketData.query.filter(MarketData.asset_type == 'stock').count()
        crypto = MarketData.query.filter(MarketData.asset_type == 'crypto').count()
        indices_count = MarketIndices.query.count()
        commodities_count = CommodityData.query.count()
        
        return jsonify({
            'stocks': stocks,
            'crypto': crypto,
            'indices': indices_count,
            'commodities': commodities_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/import', methods=['POST'])
@admin_required
def import_market_data():
    """Bulk import market data"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        asset_type = data.get('asset_type', 'stock')
        
        imported = 0
        updated = 0
        
        for item in items:
            symbol = item.get('symbol', '').upper()
            if not symbol:
                continue
                
            existing = MarketData.query.filter_by(symbol=symbol, asset_type=asset_type).first()
            
            if existing:
                existing.name = item.get('name', existing.name)
                existing.price = item.get('price', existing.price)
                existing.change = item.get('change', existing.change)
                existing.change_percent = item.get('change_percent', existing.change_percent)
                existing.volume = item.get('volume', existing.volume)
                existing.market_cap = item.get('market_cap', existing.market_cap)
                existing.last_updated = datetime.utcnow()
                updated += 1
            else:
                new_item = MarketData(
                    symbol=symbol,
                    name=item.get('name', symbol),
                    price=item.get('price', 0),
                    change=item.get('change', 0),
                    change_percent=item.get('change_percent', 0),
                    volume=item.get('volume'),
                    market_cap=item.get('market_cap'),
                    asset_type=asset_type,
                    last_updated=datetime.utcnow()
                )
                db.session.add(new_item)
                imported += 1
        
        db.session.commit()
        return jsonify({'ok': True, 'imported': imported, 'updated': updated})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/<int:id>', methods=['DELETE'])
@admin_required
def delete_market_data(id):
    """Delete a market data item"""
    try:
        item = MarketData.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# INDICES
# ============================================================================

@market_bp.route('/indices', methods=['GET'])
@admin_required
def get_indices():
    """List market indices"""
    try:
        indices = MarketIndices.query.all()
        return jsonify({
            'indices': [{
                'id': i.id,
                'symbol': i.symbol,
                'name': i.name,
                'price': float(i.price) if i.price else 0,
                'change_amount': float(i.change_amount) if i.change_amount else 0,
                'change_percent': float(i.change_percent) if i.change_percent else 0,
                'market_status': i.market_status,
                'last_updated': i.last_updated.isoformat() if i.last_updated else None
            } for i in indices]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SENTIMENT
# ============================================================================

@market_bp.route('/sentiment', methods=['GET'])
@admin_required
def get_sentiment():
    """Get market sentiment data"""
    try:
        sentiment = MarketSentiment.query.order_by(MarketSentiment.last_updated.desc()).all()
        return jsonify({
            'sentiment': [{
                'id': s.id,
                'indicator_type': s.indicator_type,
                'value': float(s.value) if s.value else 0,
                'classification': s.classification,
                'last_updated': s.last_updated.isoformat() if s.last_updated else None
            } for s in sentiment]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/sentiment', methods=['POST'])
@admin_required
def add_sentiment():
    """Add sentiment data"""
    try:
        data = request.get_json()
        s = MarketSentiment(
            indicator_type=data.get('indicator_type', 'fear_greed'),
            value=data['value'],
            classification=data.get('classification'),
            last_updated=datetime.utcnow()
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({'ok': True, 'id': s.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
