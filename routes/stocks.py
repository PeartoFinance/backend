"""
Stocks API Routes with SQLAlchemy
- Quotes, search, profile, history, movers
"""
from flask import Blueprint, request, jsonify
from sqlalchemy import desc, asc
from models.base import db
from models.market import MarketData, CompanyFinancials, MarketIssue, Dividend, AnalystRecommendation, StockPriceHistory
from models.article import NewsItem
from datetime import datetime, timedelta
from extensions import cache
from utils.validators import safe_int

stocks_bp = Blueprint('stocks', __name__)


@stocks_bp.route('/quotes', methods=['GET'])
@cache.cached(timeout=30, query_string=True)
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
        filter_condition = (MarketData.country_code == 'GLOBAL')

    prices = MarketData.query.filter(
        MarketData.symbol.in_(symbols),
        filter_condition
    ).all()
    
    return jsonify([p.to_dict() for p in prices])


@stocks_bp.route('/search', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def search_stocks():
    """Search stocks by name or symbol"""
    query = request.args.get('q', '').strip()
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
    if not query:
        return jsonify({'error': 'q parameter required'}), 400
    
    header_country = request.headers.get('X-User-Country')
    if header_country is None:
        filter_condition = (MarketData.country_code == 'GLOBAL')
    else:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    market_items = MarketData.query.filter(
        db.or_(
            MarketData.symbol.ilike(f'%{query}%'),
            MarketData.name.ilike(f'%{query}%')
        ),
        filter_condition
    ).limit(limit).all()
    
    results = [s.to_dict() for s in market_items]

    # 2. Safe Discovery: If few local results, search Yahoo for Names/Symbols ONLY.
    # We do NOT fetch prices here to prevent Yahoo from blocking us (Rate Limiting).
    if len(results) < 5 and len(query) >= 2:
        try:
            from handlers.market_data.search_handler import search_tickers
            # Fetch basic info only (fast & safe)
            yahoo_results = search_tickers(query, max_results=5)
            
            existing_symbols = {r['symbol'].upper() for r in results}
            
            for q in yahoo_results.get('quotes', []):
                sym = q.get('symbol', '').upper()
                # Only add if not already in results and looks like a valid stock
                if sym and sym not in existing_symbols:
                    results.append({
                        'symbol': sym,
                        'name': q.get('name') or q.get('shortname'),
                        'price': None,     # Price is NULL for safety. Loads on click.
                        'change': None,
                        'changePercent': None,
                        'currency': 'USD',
                        'exchange': q.get('exchange'),
                        'asset_type': 'stock',
                        'is_discovery': True, # Frontend can show "Click to Load" badge
                        'country_code': 'GLOBAL'
                    })
        except Exception as e:
            print(f"Discovery search error: {e}")

    return jsonify(results)


@stocks_bp.route('/profile/<symbol>', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
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
        filter_condition
    ).first()
    
    # 2. If not found, try to auto-import from Yahoo Finance (Live Discovery)
    if not stock:
        try:
            from handlers.market_data.stock_handler import import_stocks_to_db
            # Import as GLOBAL so everyone can see it
            import_stocks_to_db([symbol], country_code='GLOBAL')
        except Exception as e:
            # If race condition (duplicate entry), just ignore and query again
            print(f"Auto-import note for {symbol}: {e}")
            
        # Query again - whether we added it or someone else did
        stock = MarketData.query.filter(
            MarketData.symbol == symbol,
            filter_condition
        ).first()
    
    if not stock:
        return jsonify({'error': 'Stock not found'}), 404
    
    data = stock.to_dict()
    
    # 1. Get Market Issues (Active ones)
    issues = MarketIssue.query.filter_by(symbol=symbol, is_active=True).order_by(MarketIssue.issue_date.desc()).all()
    data['marketIssues'] = [i.to_dict() for i in issues]
    
    # 2. Get Related News
    news = NewsItem.query.filter_by(related_symbol=symbol).order_by(NewsItem.published_at.desc()).limit(5).all()
    if not news:
        news = NewsItem.query.filter(
            NewsItem.title.ilike(f'%{symbol}%'),
            NewsItem.curated_status == 'published'
        ).order_by(NewsItem.published_at.desc()).limit(5).all()
    
    data['news'] = [n.to_dict() for n in news]
    
    return jsonify(data)


@stocks_bp.route('/financials/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_financials(symbol):
    """Get full financial statements for a symbol"""
    symbol = symbol.upper()
    period = request.args.get('period', 'annual')
    
    financials = CompanyFinancials.query.filter_by(
        symbol=symbol, 
        period=period
    ).order_by(CompanyFinancials.fiscal_date_ending.desc()).all()
    
    return jsonify([f.to_dict() for f in financials])


@stocks_bp.route('/financials/<symbol>/statements', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_financial_statements(symbol):
    """
    Get comprehensive financial statements from database.
    Falls back to yfinance sync if no data exists.
    
    Query params:
        statement_type: 'income', 'balance', 'cash_flow', 'ratios' (default: 'income')
        period: 'annual', 'quarterly' (default: 'annual')
    """
    from handlers.market_data.financial_handler import get_financial_statements
    
    symbol = symbol.upper()
    statement_type = request.args.get('statement_type', 'income')
    period = request.args.get('period', 'annual')
    
    data = get_financial_statements(symbol, statement_type, period)
    
    if 'error' in data:
        return jsonify(data), 400
    
    data['symbol'] = symbol
    return jsonify(data)


@stocks_bp.route('/forecast/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_forecast(symbol):
    """
    Get comprehensive analyst forecast data including:
    - Price targets (low, mean, high, upside)
    - Analyst consensus (Strong Buy/Buy/Hold/Sell counts)
    - Earnings estimates (Revenue & EPS projections)
    - Recommendation trends (historical ratings by month)
    """
    symbol = symbol.upper()
    from handlers.market_data.forecast_handler import get_detailed_forecast
    
    forecast = get_detailed_forecast(symbol)
    if not forecast or (not forecast.get('priceTarget', {}).get('mean') and not forecast.get('earningsEstimates', {}).get('annual')):
        return jsonify({'error': 'Forecast data not found. Try syncing from admin panel.'}), 404
        
    return jsonify(forecast)


@stocks_bp.route('/statistics/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_statistics(symbol):
    """Get detailed technical and fundamental statistics for a symbol"""
    symbol = symbol.upper()
    stock = MarketData.query.filter_by(symbol=symbol).first()
    
    if not stock:
        return jsonify({'error': 'Asset not found'}), 404
        
    stats = {
        'symbol': stock.symbol,
        'marketCap': float(stock.market_cap) if stock.market_cap else None,
        'peRatio': float(stock.pe_ratio) if stock.pe_ratio else None,
        'forwardPe': float(stock.forward_pe) if stock.forward_pe else None,
        'eps': float(stock.eps) if stock.eps else None,
        'beta': float(stock.beta) if stock.beta else None,
        'dividendYield': float(stock.dividend_yield) if stock.dividend_yield else None,
        'dividendRate': float(stock.dividend_rate) if stock.dividend_rate else None,
        'sharesOutstanding': stock.shares_outstanding,
        'floatShares': stock.float_shares,
        'bookValue': float(stock.book_value) if stock.book_value else None,
        'priceToBook': float(stock.price_to_book) if stock.price_to_book else None,
        'shortRatio': float(stock.short_ratio) if stock.short_ratio else None,
        'high52w': float(stock._52_week_high) if stock._52_week_high else None,
        'low52w': float(stock._52_week_low) if stock._52_week_low else None,
        'avgVolume': stock.avg_volume
    }
    
    return jsonify(stats)


@stocks_bp.route('/dividends/<symbol>', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_stock_dividends(symbol):
    """Get dividend history for a specific symbol"""
    symbol = symbol.upper()
    dividends = Dividend.query.filter_by(symbol=symbol).order_by(Dividend.created_at.desc()).all()
    
    return jsonify([d.to_dict() for d in dividends])


@stocks_bp.route('/directory', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_business_directory():
    """List all businesses marked as 'is_listed' for the public directory"""
    try:
        from handlers.market_data.business_handler import get_business_directory
        
        search = request.args.get('q', '')
        header_country = request.headers.get('X-User-Country', 'US')
        # Safe conversion: Returns 20 if invalid characters sent
        limit = min(safe_int(request.args.get('limit'), 20), 100)
        
        businesses = get_business_directory(search=search, country=header_country, limit=limit)
        return jsonify(businesses)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@stocks_bp.route('/movers', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_movers():
    """Get top gainers and losers - cached for 5 minutes"""
    mover_type = request.args.get('type', 'both')
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
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
            MarketData.is_listed == True,
            MarketData.change_percent > 0,
            filter_condition
        ).order_by(desc(MarketData.change_percent)).limit(limit).all()
        result['gainers'] = [g.to_dict() for g in gainers]
    
    if mover_type in ('losers', 'both'):
        losers = MarketData.query.filter(
            MarketData.asset_type == 'stock',
            MarketData.is_listed == True,
            MarketData.change_percent < 0,
            filter_condition
        ).order_by(asc(MarketData.change_percent)).limit(limit).all()
        result['losers'] = [l.to_dict() for l in losers]
    
    return jsonify(result)


@stocks_bp.route('/most-active', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_most_active():
    """Get most actively traded stocks - cached for 5 minutes"""
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
    header_country = request.headers.get('X-User-Country')
    if header_country:
        country = header_country.strip().upper()
        filter_condition = MarketData.country_code.in_([country, 'GLOBAL'])
    else:
        filter_condition = (MarketData.country_code == 'GLOBAL')

    stocks = MarketData.query.filter(
        MarketData.asset_type == 'stock',
        MarketData.is_listed == True,
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
@cache.cached(timeout=300, query_string=True)
def get_etfs():
    """List all ETFs with optional search and pagination"""
    query = request.args.get('q', '').strip()
    # Safe conversion: Returns 20 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 20), 100)
    # Safe conversion: Returns page 1 if invalid characters sent
    page = max(safe_int(request.args.get('page'), 1), 1)
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
@cache.cached(timeout=300, query_string=True)
def get_etf_movers():
    """Get top ETF gainers and losers"""
    # Safe conversion: Returns 10 if invalid characters sent
    limit = min(safe_int(request.args.get('limit'), 10), 50)
    
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


# Simple in-memory cache for history to prevent Yahoo rate limits
# Format: { 'SYMBOL_PERIOD_INTERVAL': (timestamp, data) }
history_cache = {}

@stocks_bp.route('/history/<symbol>', methods=['GET'])
def get_history(symbol):
    """Get price history for a symbol (Stock, ETF, or Crypto)"""
    try:
        from handlers.market_data.stock_handler import get_stock_history, save_stock_history_to_db
        import time
        
        symbol = symbol.upper()
        period = request.args.get('period', '1mo')
        interval = request.args.get('interval', '1d')
        
        # SMART VALIDATION: Yahoo Finance limits 1m data to 7 days, and 2m-90m data to 60 days.
        # If the frontend asks for a period that doesn't exist for that interval, Yahoo returns 404.
        if interval == '1m' and period not in ('1d', '5d', '7d'):
            period = '1d' # Auto-adjust to 1 day if 1-minute interval is selected
        elif interval in ('2m', '5m', '15m', '30m', '90m') and period not in ('1d', '5d', '1mo'):
            if 'y' in period or 'max' in period: # If user tried to get years of intraday data
                period = '1mo' # Max reliable period for these intervals
        
        # 1. Check In-Memory Cache first (Fastest, handles 1000s of users)
        cache_key = f"{symbol}_{period}_{interval}"
        now = time.time()
        if cache_key in history_cache:
            cache_time, cached_data = history_cache[cache_key]
            if now - cache_time < 300:  # 5 minute cache
                return jsonify({
                    'symbol': symbol,
                    'period': period,
                    'interval': interval,
                    'data': cached_data,
                    'source': 'memory_cache'
                })
        
        # 2. Try to get from Database (Only for daily data)
        if interval == '1d':
            days_map = {'1mo': 30, '3mo': 90, '6mo': 180, '1y': 365, '2y': 730, '5y': 1825}
            days_back = days_map.get(period, 30)
            start_date = datetime.utcnow() - timedelta(days=days_back)
            
            db_history = StockPriceHistory.query.filter(
                StockPriceHistory.symbol == symbol,
                StockPriceHistory.interval == interval,
                StockPriceHistory.date >= start_date.date()
            ).order_by(StockPriceHistory.date.asc()).all()
            
            if len(db_history) >= (days_back * 0.5):
                data = [h.to_dict() for h in db_history]
                # Also save to memory cache for the next user
                history_cache[cache_key] = (now, data)
                return jsonify({
                    'symbol': symbol,
                    'period': period,
                    'interval': interval,
                    'data': data,
                    'source': 'database'
                })

        # 3. Fallback to Yahoo Finance
        history = get_stock_history(symbol, period=period, interval=interval)
        
        if not history:
            return jsonify({'error': 'No history found for this symbol'}), 404
            
        # 4. Save to DB (if daily) and Memory Cache (always)
        if interval == '1d':
            save_stock_history_to_db(symbol, history, interval=interval)
        
        history_cache[cache_key] = (now, history)
            
        return jsonify({
            'symbol': symbol,
            'period': period,
            'interval': interval,
            'data': history,
            'source': 'yahoo'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
