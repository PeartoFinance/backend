"""
Admin Market Routes - Market data management
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, MarketData, MarketIndices, MarketSentiment, CryptoMarketData, CommodityData, MarketIssue
from datetime import datetime

market_bp = Blueprint('admin_market', __name__)


@market_bp.route('/market-data', methods=['GET'])
@permission_required("market_data")
def get_market_data():
    """List market data with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', request.args.get('limit', 100, type=int), type=int)
        
        country = getattr(request, 'user_country', 'US')
        query = MarketData.query.filter(
            MarketData.asset_type == asset_type,
            (MarketData.country_code == country) | (MarketData.country_code == 'GLOBAL')
        )
        if search:
            query = query.filter(
                db.or_(
                    MarketData.symbol.ilike(f'%{search}%'),
                    MarketData.name.ilike(f'%{search}%')
                )
            )
        
        paginated_data = query.order_by(MarketData.symbol).paginate(
            page=page, per_page=per_page, error_out=False
        )
        items = paginated_data.items
        
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
                'pe_ratio': float(m.pe_ratio) if m.pe_ratio else None,
                'eps': float(m.eps) if m.eps else None,
                'sector': m.sector,
                'industry': m.industry,
                'exchange': m.exchange,
                'currency': m.currency,
                'high_52w': float(m._52_week_high) if m._52_week_high else None,
                'low_52w': float(m._52_week_low) if m._52_week_low else None,
                'open_price': float(m.open_price) if m.open_price else None,
                'previous_close': float(m.previous_close) if m.previous_close else None,
                'day_high': float(m.day_high) if m.day_high else None,
                'day_low': float(m.day_low) if m.day_low else None,
                'avg_volume': m.avg_volume,
                'beta': float(m.beta) if m.beta else None,
                'dividend_yield': float(m.dividend_yield) if m.dividend_yield else None,
                'dividend_rate': float(m.dividend_rate) if m.dividend_rate else None,
                'shares_outstanding': m.shares_outstanding,
                'website': m.website,
                'logo_url': m.logo_url,
                'asset_type': m.asset_type,
                'is_listed': m.is_listed,
                'is_featured': m.is_featured,
                'last_updated': m.last_updated.isoformat() if m.last_updated else None
            } for m in items],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/stats', methods=['GET'])
@permission_required("market_data")
def get_market_stats():
    """Get market data statistics"""
    try:
        country = getattr(request, 'user_country', 'US')
        stocks = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            (MarketData.country_code == country) | (MarketData.country_code == 'GLOBAL')
        ).count()
        crypto = MarketData.query.filter(
            MarketData.asset_type == 'crypto',
            (MarketData.country_code == country) | (MarketData.country_code == 'GLOBAL')
        ).count()
        indices_count = MarketIndices.query.filter(
            (MarketIndices.country_code == country) | (MarketIndices.country_code == 'GLOBAL')
        ).count()
        commodities_count = CommodityData.query.filter(
            (CommodityData.country_code == country) | (CommodityData.country_code == 'GLOBAL')
        ).count()
        
        return jsonify({
            'stocks': stocks,
            'crypto': crypto,
            'indices': indices_count,
            'commodities': commodities_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/import', methods=['POST'])
@permission_required("market_data")
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
                
            country_code = item.get('country_code') or getattr(request, 'user_country', None) or 'GLOBAL'
            existing = MarketData.query.filter_by(
                symbol=symbol, 
                asset_type=asset_type,
                country_code=country_code
            ).first()
            
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
                    country_code=country_code,
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
@permission_required("market_data")
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
@permission_required("market_data")
def get_indices():
    """List market indices"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        
        country = getattr(request, 'user_country', 'US')
        query = MarketIndices.query.filter(
            (MarketIndices.country_code == country) | (MarketIndices.country_code == 'GLOBAL')
        )
        
        if search:
            query = query.filter(
                db.or_(
                    MarketIndices.symbol.ilike(f'%{search}%'),
                    MarketIndices.name.ilike(f'%{search}%')
                )
            )
            
        paginated_data = query.order_by(MarketIndices.symbol).paginate(
            page=page, per_page=per_page, error_out=False
        )
        indices = paginated_data.items
        
        return jsonify({
            'items': [{
                'id': i.id,
                'symbol': i.symbol,
                'name': i.name,
                'price': float(i.price) if i.price else 0,
                'change_amount': float(i.change_amount) if i.change_amount else 0,
                'change_percent': float(i.change_percent) if i.change_percent else 0,
                'previous_close': float(i.previous_close) if i.previous_close else None,
                'day_high': float(i.day_high) if i.day_high else None,
                'day_low': float(i.day_low) if i.day_low else None,
                'year_high': float(i.year_high) if i.year_high else None,
                'year_low': float(i.year_low) if i.year_low else None,
                'market_status': i.market_status,
                'country_code': i.country_code,
                'last_updated': i.last_updated.isoformat() if i.last_updated else None
            } for i in indices],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# STOCK OFFERS (IPOs)
# ============================================================================

@market_bp.route('/stock-offers', methods=['GET'])
@permission_required("market_data")
def get_stock_offers():
    """List stock offers (IPOs, FPOs)"""
    try:
        from models import StockOffer
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        
        country = getattr(request, 'user_country', 'US')
        query = StockOffer.query.filter(
            (StockOffer.country_code == country) | (StockOffer.country_code == 'GLOBAL')
        )
        if search:
            query = query.filter(
                db.or_(
                    StockOffer.symbol.ilike(f'%{search}%'),
                    StockOffer.company_name.ilike(f'%{search}%')
                )
            )
            
        paginated_data = query.order_by(StockOffer.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'items': [o.to_dict() for o in paginated_data.items],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 200


# ============================================================================
# COMMODITIES
# ============================================================================

@market_bp.route('/commodities', methods=['GET'])
@permission_required("market_data")
def get_commodities():
    """List all commodities"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        search = request.args.get('search', '')
        category = request.args.get('category', 'all')
        
        country = getattr(request, 'user_country', 'US')
        query = CommodityData.query.filter(
            (CommodityData.country_code == country) | (CommodityData.country_code == 'GLOBAL')
        )

        metals_symbols = ['GC=F', 'SI=F', 'PL=F', 'PA=F', 'HG=F']
        energy_symbols = ['CL=F', 'BZ=F', 'NG=F', 'RB=F', 'HO=F']
        
        if category == 'metals':
            query = query.filter(CommodityData.symbol.in_(metals_symbols))
        elif category == 'energy':
            query = query.filter(CommodityData.symbol.in_(energy_symbols))
        elif category == 'agriculture':
            query = query.filter(~CommodityData.symbol.in_(metals_symbols + energy_symbols + ['LE=F', 'HE=F']))

        if search:
            query = query.filter(
                db.or_(
                    CommodityData.symbol.ilike(f'%{search}%'),
                    CommodityData.name.ilike(f'%{search}%')
                )
            )
            
        paginated_data = query.order_by(CommodityData.symbol).paginate(
            page=page, per_page=per_page, error_out=False
        )
        commodities = paginated_data.items
        
        return jsonify({
            'items': [{
                'id': c.id,
                'symbol': c.symbol,
                'name': c.name,
                'price': float(c.price) if c.price else 0,
                'change': float(c.change) if c.change else 0,
                'change_percent': float(c.change_percent) if c.change_percent else 0,
                'day_high': float(c.day_high) if c.day_high else None,
                'day_low': float(c.day_low) if c.day_low else None,
                'year_high': float(c.year_high) if c.year_high else None,
                'year_low': float(c.year_low) if c.year_low else None,
                'unit': c.unit,
                'currency': c.currency,
                'last_updated': c.last_updated.isoformat() if c.last_updated else None
            } for c in commodities],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# EARNINGS CALENDAR
# ============================================================================

@market_bp.route('/earnings-calendar', methods=['GET'])
@permission_required("market_data")
def get_earnings_calendar():
    """List earnings calendar events from database"""
    try:
        from models import EarningsCalendar
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', request.args.get('limit', 50, type=int), type=int)
        search = request.args.get('search', '')
        
        country = getattr(request, 'user_country', 'US')
        query = EarningsCalendar.query.filter(
            (EarningsCalendar.country_code == country) | (EarningsCalendar.country_code == 'GLOBAL')
        )
        if search:
            query = query.filter(
                db.or_(
                    EarningsCalendar.symbol.ilike(f'%{search}%'),
                    EarningsCalendar.company_name.ilike(f'%{search}%')
                )
            )
            
        paginated_data = query.order_by(EarningsCalendar.earnings_date.asc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        events = paginated_data.items
        
        return jsonify({
            'items': [{
                'id': e.id,
                'symbol': e.symbol,
                'company_name': e.company_name,
                'earnings_date': e.earnings_date.isoformat() if e.earnings_date else None,
                'eps_estimate': float(e.eps_estimate) if e.eps_estimate else None,
                'eps_actual': float(e.eps_actual) if e.eps_actual else None,
                'surprise_percent': float(e.surprise_percent) if e.surprise_percent else None,
                'revenue_estimate': e.revenue_estimate,
                'revenue_actual': e.revenue_actual,
                'market_cap': e.market_cap,
                'before_after_market': e.before_after_market,
            } for e in events],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 200


# ============================================================================
# SENTIMENT
# ============================================================================

@market_bp.route('/sentiment', methods=['GET'])
@permission_required("market_data")
def get_sentiment():
    """Get market sentiment data"""
    try:
        country = getattr(request, 'user_country', 'US')
        sentiment = MarketSentiment.query.filter(
            (MarketSentiment.country_code == country) | (MarketSentiment.country_code == 'GLOBAL')
        ).order_by(MarketSentiment.last_updated.desc()).all()
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
@permission_required("market_data")
def add_sentiment():
    """Add sentiment data"""
    try:
        data = request.get_json()
        s = MarketSentiment(
            indicator_type=data.get('indicator_type', 'fear_greed'),
            value=data['value'],
            classification=data.get('classification'),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US')),
            last_updated=datetime.utcnow()
        )
        db.session.add(s)
        db.session.commit()
        return jsonify({'ok': True, 'id': s.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# YFINANCE IMPORT ROUTES
# ============================================================================

@market_bp.route('/import/stocks', methods=['POST'])
@permission_required("market_data")
def import_stocks_yfinance():
    """Import stocks from yfinance by symbols"""
    try:
        from handlers.market_data.stock_handler import import_stocks_to_db
        
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'symbols array required'}), 400
        
        country = data.get('country_code') or getattr(request, 'user_country', None) or 'GLOBAL'
        result = import_stocks_to_db(symbols, country_code=country)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
            'message': f"Processed {len(symbols)} symbols for {country}"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/crypto', methods=['POST'])
@permission_required("market_data")
def import_crypto_yfinance():
    """Import cryptocurrencies from yfinance"""
    try:
        from handlers.market_data.crypto_handler import import_cryptos_to_db, TOP_CRYPTOS
        
        data = request.get_json() or {}
        symbols = data.get('symbols', TOP_CRYPTOS)
        
        country = data.get('country_code') or getattr(request, 'user_country', None) or 'GLOBAL'
        result = import_cryptos_to_db(symbols, country_code=country)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
            'message': f"Processed {len(symbols)} cryptos"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/indices', methods=['POST'])
@permission_required("market_data")
def import_indices_yfinance():
    """Import market indices from yfinance"""
    try:
        from handlers.market_data.index_handler import import_indices_to_db, MAJOR_INDICES
        
        data = request.get_json() or {}
        symbols = data.get('symbols', list(MAJOR_INDICES.keys()))
        
        country = data.get('country_code') or getattr(request, 'user_country', None) or 'GLOBAL'
        result = import_indices_to_db(symbols, country_code=country)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
            'message': f"Processed {len(symbols)} indices"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/commodities', methods=['POST'])
@permission_required("market_data")
def import_commodities_yfinance():
    """Import commodities from yfinance"""
    try:
        from handlers.market_data.commodity_handler import import_commodities_to_db, COMMODITIES
        
        data = request.get_json() or {}
        symbols = data.get('symbols', list(COMMODITIES.keys()))
        
        country = data.get('country_code') or getattr(request, 'user_country', None) or 'GLOBAL'
        result = import_commodities_to_db(symbols, country_code=country)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
            'message': f"Processed {len(symbols)} commodities"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/screener', methods=['POST'])
@permission_required("market_data")
def import_from_screener():
    """Import stocks from a predefined screener"""
    try:
        from handlers.market_data.screener_handler import import_screener_to_db, PREDEFINED_SCREENERS
        
        data = request.get_json()
        screener = data.get('screener', 'day_gainers')
        count = min(int(data.get('count', 50)), 100)
        
        if screener not in PREDEFINED_SCREENERS:
            return jsonify({
                'error': f"Unknown screener. Valid options: {', '.join(PREDEFINED_SCREENERS)}"
            }), 400
        
        result = import_screener_to_db(screener, count)
        return jsonify({
            'ok': True,
            'screener': screener,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/calendar/earnings', methods=['POST'])
@permission_required("market_data")
def import_earnings_calendar():
    """Import earnings calendar from yfinance"""
    try:
        from handlers.market_data.calendar_handler import import_earnings_to_db
        
        data = request.get_json() or {}
        start = data.get('start')
        end = data.get('end')
        limit = min(int(data.get('limit', 50)), 100)
        
        result = import_earnings_to_db(start, end, limit)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/import/calendar/ipos', methods=['POST'])
@permission_required("market_data")
def import_ipo_calendar():
    """Import IPO calendar from yfinance"""
    try:
        from handlers.market_data.calendar_handler import import_ipos_to_db
        
        data = request.get_json() or {}
        start = data.get('start')
        end = data.get('end')
        limit = min(int(data.get('limit', 50)), 100)
        
        result = import_ipos_to_db(start, end, limit)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/search', methods=['GET'])
@permission_required("market_data")
def search_market_data():
    """Search for tickers using yfinance"""
    try:
        from handlers.market_data.search_handler import search_tickers
        
        query = request.args.get('q', '')
        max_results = min(int(request.args.get('limit', 10)), 20)
        
        if not query:
            return jsonify({'error': 'q parameter required'}), 400
        
        results = search_tickers(query, max_results=max_results)
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/refresh/<symbol>', methods=['POST'])
@permission_required("market_data")
def refresh_symbol(symbol):
    """Refresh data for a single symbol from yfinance"""
    try:
        from handlers.market_data.stock_handler import import_stocks_to_db
        
        result = import_stocks_to_db([symbol])
        return jsonify({
            'ok': True,
            'symbol': symbol,
            'updated': result.get('updated', 0) + result.get('imported', 0),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/market-data/history/<symbol>', methods=['GET'])
@permission_required("market_data")
def get_symbol_history(symbol):
    """Get price history for a symbol from yfinance"""
    try:
        from handlers.market_data.stock_handler import get_stock_history, save_stock_history_to_db
        
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # 1. Fetch live data
        history = get_stock_history(symbol, period=period, interval=interval)
        
        # 2. Save to DB for future analysis
        if history:
            save_stock_history_to_db(symbol, history, interval=interval)
            
        return jsonify({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': history,
            'stored': True
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/screeners', methods=['GET'])
@permission_required("market_data")
def get_available_screeners():
    """Get list of available predefined screeners"""
    try:
        from handlers.market_data.screener_handler import PREDEFINED_SCREENERS
        return jsonify({'screeners': PREDEFINED_SCREENERS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/screener/<screener_name>', methods=['GET'])
@permission_required("market_data")
def run_screener(screener_name):
    """Run a screener and get results (without importing)"""
    try:
        from handlers.market_data.screener_handler import run_predefined_screen, PREDEFINED_SCREENERS
        
        if screener_name not in PREDEFINED_SCREENERS:
            return jsonify({'error': 'Unknown screener'}), 400
        
        limit = min(int(request.args.get('limit', 25)), 100)
        results = run_predefined_screen(screener_name, limit)
        
        return jsonify({
            'screener': screener_name,
            'count': len(results),
            'results': results,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# DIVIDEND ROUTES
# ============================================================================

@market_bp.route('/dividends', methods=['GET'])
@permission_required("market_data")
def get_dividends():
    """Get all dividends from database"""
    try:
        from models import Dividend
        from sqlalchemy import desc
        
        status = request.args.get('status')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', request.args.get('limit', 100, type=int), type=int)
        search = request.args.get('search', '')
        country = getattr(request, 'user_country', 'US')
        
        query = Dividend.query.filter(
            (Dividend.country_code == country) | (Dividend.country_code == 'GLOBAL')
        )
        if status:
            query = query.filter(Dividend.status == status)
        if search:
            query = query.filter(
                db.or_(
                    Dividend.symbol.ilike(f'%{search}%'),
                    Dividend.company_name.ilike(f'%{search}%')
                )
            )
        
        paginated_data = query.order_by(desc(Dividend.created_at)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        dividends = paginated_data.items
        
        return jsonify({
            'items': [d.to_dict() for d in dividends],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 200


@market_bp.route('/import/dividends', methods=['POST'])
@permission_required("market_data")
def import_dividends_yfinance():
    """Import dividend data from yfinance"""
    try:
        from handlers.market_data.dividend_handler import import_dividends_to_db, DIVIDEND_STOCKS
        
        data = request.get_json() or {}
        symbols = data.get('symbols', DIVIDEND_STOCKS)
        
        result = import_dividends_to_db(symbols)
        return jsonify({
            'ok': True,
            'imported': result.get('imported', 0),
            'updated': result.get('updated', 0),
            'errors': result.get('errors', 0),
            'message': f"Processed {len(symbols)} dividend stocks"
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/dividends/calendar', methods=['GET'])
@permission_required("market_data")
def get_dividend_calendar():
    """Get upcoming ex-dividend dates"""
    try:
        from handlers.market_data.dividend_handler import get_ex_dividend_calendar
        
        calendar = get_ex_dividend_calendar()
        return jsonify({
            'items': calendar,
            'total': len(calendar)
        })
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 200


@market_bp.route('/dividends/<int:id>', methods=['DELETE'])
@permission_required("market_data")
def delete_dividend(id):
    """Delete a dividend entry"""
    try:
        from models import Dividend
        
        dividend = Dividend.query.get(id)
        if not dividend:
            return jsonify({'error': 'Dividend not found'}), 404
        
        db.session.delete(dividend)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'Dividend deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# BULK TRANSACTION ROUTES
# ============================================================================

@market_bp.route('/bulk-transactions', methods=['GET'])
@permission_required("market_data")
def get_bulk_transactions():
    """Get all bulk transactions from database"""
    try:
        from models import BulkTransaction
        from sqlalchemy import desc
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', request.args.get('limit', 100, type=int), type=int)
        symbol = request.args.get('symbol')
        search = request.args.get('search', '')
        country = getattr(request, 'user_country', 'US')
        
        query = BulkTransaction.query.filter(
            (BulkTransaction.country_code == country) | (BulkTransaction.country_code == 'GLOBAL')
        )
        if symbol:
            query = query.filter(BulkTransaction.symbol == symbol.upper())
        if search:
            query = query.filter(
                db.or_(
                    BulkTransaction.symbol.ilike(f'%{search}%'),
                    BulkTransaction.company_name.ilike(f'%{search}%')
                )
            )
        
        paginated_data = query.order_by(desc(BulkTransaction.transaction_date)).paginate(
            page=page, per_page=per_page, error_out=False
        )
        transactions = paginated_data.items
        
        return jsonify({
            'items': [t.to_dict() for t in transactions],
            'total': paginated_data.total,
            'pages': paginated_data.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e), 'items': []}), 200


@market_bp.route('/bulk-transactions', methods=['POST'])
@permission_required("market_data")
def add_bulk_transaction():
    """Add a bulk transaction manually"""
    try:
        from models import BulkTransaction
        
        data = request.get_json()
        
        tx = BulkTransaction(
            symbol=data['symbol'].upper(),
            company_name=data.get('companyName'),
            transaction_date=datetime.fromisoformat(data['transactionDate']) if data.get('transactionDate') else datetime.utcnow(),
            buyer_broker=data.get('buyerBroker'),
            seller_broker=data.get('sellerBroker'),
            quantity=data.get('quantity'),
            price=data.get('price'),
            amount=data.get('amount'),
            change_percent=data.get('changePercent'),
            transaction_type=data.get('transactionType', 'bulk'),
            exchange=data.get('exchange'),
            country_code=data.get('countryCode', getattr(request, 'user_country', 'US'))
        )
        
        db.session.add(tx)
        db.session.commit()
        
        return jsonify({'ok': True, 'id': tx.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@market_bp.route('/bulk-transactions/<int:id>', methods=['DELETE'])
@permission_required("market_data")
def delete_bulk_transaction(id):
    """Delete a bulk transaction"""
    try:
        from models import BulkTransaction
        
        tx = BulkTransaction.query.get(id)
        if not tx:
            return jsonify({'error': 'Transaction not found'}), 404
        
        db.session.delete(tx)
        db.session.commit()
        return jsonify({'ok': True, 'message': 'Transaction deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@market_bp.route('/dividend-stocks', methods=['GET'])
@permission_required("market_data")
def get_dividend_stock_list():
    """Get list of popular dividend stocks for import"""
    try:
        from handlers.market_data.dividend_handler import DIVIDEND_STOCKS
        return jsonify({'symbols': DIVIDEND_STOCKS})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============================================================================
# BUSINESS PROFILE ROUTES
# ============================================================================

@market_bp.route('/business/sync-financials', methods=['POST'])
@permission_required("market_data")
def admin_sync_financials():
    """
    Sync financial statements for a symbol.
    Syncs both annual and quarterly data by default.
    """
    try:
        from handlers.market_data.financial_handler import sync_financials, sync_all_financials
        data = request.get_json()
        symbol = data.get('symbol')
        period = data.get('period')  # 'annual', 'quarterly', or None for both
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
        
        if period:
            result = sync_financials(symbol, period)
        else:
            result = sync_all_financials(symbol)
            
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/bulk-sync-financials', methods=['POST'])
@permission_required("market_data")
def admin_bulk_sync_financials():
    """
    Sync financials for multiple symbols.
    POST body: { "symbols": ["AAPL", "MSFT", "GOOGL"] }
    """
    try:
        from handlers.market_data.financial_handler import sync_all_financials
        data = request.get_json()
        symbols = data.get('symbols', [])
        
        if not symbols:
            return jsonify({'error': 'Symbols array is required'}), 400
        
        results = {}
        success_count = 0
        error_count = 0
        
        for symbol in symbols:
            try:
                result = sync_all_financials(symbol)
                results[symbol] = result
                if result.get('status') in ['success', 'partial']:
                    success_count += 1
                else:
                    error_count += 1
            except Exception as e:
                results[symbol] = {'status': 'error', 'message': str(e)}
                error_count += 1
        
        return jsonify({
            'ok': True,
            'synced': success_count,
            'errors': error_count,
            'results': results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/sync-forecast', methods=['POST'])
@permission_required("market_data")
def admin_sync_forecast():
    """Sync analyst forecast data for a symbol"""
    try:
        from handlers.market_data.forecast_handler import sync_forecast_data
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        result = sync_forecast_data(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/sync-news', methods=['POST'])
@permission_required("market_data")
def admin_sync_news():
    """Sync latest news for a symbol from yfinance"""
    try:
        from handlers.market_data.stock_handler import sync_stock_news
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        result = sync_stock_news(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/toggle-listing', methods=['POST'])
@permission_required("market_data")
def admin_toggle_listing():
    """Toggle business listing status"""
    try:
        from handlers.market_data.business_handler import toggle_business_listing
        data = request.get_json()
        symbol = data.get('symbol')
        is_listed = data.get('is_listed', False)
        
        if not symbol:
            return jsonify({'error': 'Symbol is required'}), 400
            
        result = toggle_business_listing(symbol, is_listed)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/add-issue', methods=['POST'])
@permission_required("market_data")
def admin_add_issue():
    """Add a market issue/alert for a business"""
    try:
        from handlers.market_data.business_handler import add_market_issue
        data = request.get_json()
        symbol = data.get('symbol')
        title = data.get('title')
        description = data.get('description')
        severity = data.get('severity', 'info')
        
        if not symbol or not title:
            return jsonify({'error': 'Symbol and title are required'}), 400
            
        result = add_market_issue(symbol, title, description, severity)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/issues/<symbol>', methods=['GET'])
@permission_required("market_data")
def admin_get_issues(symbol):
    """Get all market issues for a business"""
    try:
        issues = MarketIssue.query.filter_by(symbol=symbol).order_by(MarketIssue.issue_date.desc()).all()
        return jsonify([i.to_dict() for i in issues])
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@market_bp.route('/business/issues/<int:issue_id>', methods=['DELETE'])
@permission_required("market_data")
def admin_delete_issue(issue_id):
    """Resolve/Delete a market issue"""
    try:
        from handlers.market_data.business_handler import resolve_market_issue
        result = resolve_market_issue(issue_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
