"""
Market Data Update Jobs
Periodic jobs to refresh market data from yfinance
"""
import logging
from datetime import datetime
from typing import Dict, Any

logger = logging.getLogger(__name__)


def get_app():
    """Get Flask app instance for use outside request context"""
    from app import app
    return app


def update_all_stocks() -> Dict[str, Any]:
    """
    Update all stocks in the database with latest prices from yfinance.
    Fetches symbols from MarketData table and refreshes each one.
    """
    logger.info("Starting stock update job")
    start_time = datetime.utcnow()
    
    try:
        from models import db, MarketData
        from handlers.market_data import import_stocks_to_db
        
        app = get_app()
        with app.app_context():
            # Get all stock symbols currently in database
            stocks = MarketData.query.filter_by(asset_type='stock').all()
            
            if not stocks:
                logger.info("No stocks to update")
                return {'status': 'ok', 'updated': 0}

            # Group stocks by country code to update them independently
            from collections import defaultdict
            stocks_by_country = defaultdict(list)
            for s in stocks:
                stocks_by_country[s.country_code].append(s.symbol)
            
            total_updated = 0
            total_errors = 0
            
            for country, symbols in stocks_by_country.items():
                # Update in batches of 50
                batch_size = 50
                for i in range(0, len(symbols), batch_size):
                    batch = symbols[i:i + batch_size]
                    result = import_stocks_to_db(batch, country_code=country)
                    total_updated += result.get('updated', 0)
                    total_errors += result.get('errors', 0)
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Stock update complete: {total_updated} updated, {total_errors} errors in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'updated': total_updated,
                'errors': total_errors,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Stock update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_all_crypto() -> Dict[str, Any]:
    """
    Update all cryptocurrency prices from yfinance.
    """
    logger.info("Starting crypto update job")
    start_time = datetime.utcnow()
    
    try:
        from handlers.market_data import import_cryptos_to_db, TOP_CRYPTOS
        
        app = get_app()
        with app.app_context():
            # Crypto is always GLOBAL
            result = import_cryptos_to_db(TOP_CRYPTOS)
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Crypto update complete: {result.get('updated', 0)} updated in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                **result,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Crypto update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_all_indices() -> Dict[str, Any]:
    """
    Update all market indices from yfinance.
    """
    logger.info("Starting indices update job")
    start_time = datetime.utcnow()
    
    try:
        from handlers.market_data import import_indices_to_db, MAJOR_INDICES
        
        app = get_app()
        with app.app_context():
            symbols = list(MAJOR_INDICES.keys())
            result = import_indices_to_db(symbols, country_code='GLOBAL')
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Indices update complete: {result.get('updated', 0)} updated in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                **result,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Indices update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_all_commodities() -> Dict[str, Any]:
    """
    Update all commodity prices from yfinance.
    """
    logger.info("Starting commodities update job")
    start_time = datetime.utcnow()
    
    try:
        from handlers.market_data import import_commodities_to_db, COMMODITIES
        
        app = get_app()
        with app.app_context():
            symbols = list(COMMODITIES.keys())
            result = import_commodities_to_db(symbols, country_code='GLOBAL')
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Commodities update complete: {result.get('updated', 0)} updated in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                **result,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Commodities update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_earnings_calendar() -> Dict[str, Any]:
    """
    Update earnings calendar from yfinance.
    Runs daily to fetch upcoming earnings announcements.
    """
    logger.info("Starting earnings calendar update job")
    
    try:
        from handlers.market_data import import_earnings_to_db
        
        app = get_app()
        with app.app_context():
            result = import_earnings_to_db(limit=100)
            logger.info(f"Earnings calendar update complete: {result}")
            return {'status': 'ok', **result}
    except Exception as e:
        logger.error(f"Earnings calendar update failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_dividends() -> Dict[str, Any]:
    """
    Update dividend data from yfinance.
    Runs daily to fetch ex-dividend dates and yields.
    """
    logger.info("Starting dividends update job")
    
    try:
        from handlers.market_data import import_dividends_to_db, DIVIDEND_STOCKS
        
        app = get_app()
        with app.app_context():
            result = import_dividends_to_db(DIVIDEND_STOCKS)
            logger.info(f"Dividends update complete: {result}")
            return {'status': 'ok', **result}
    except Exception as e:
        logger.error(f"Dividends update failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_business_profiles() -> Dict[str, Any]:
    """
    Update Financials and Forecast data for all 'is_listed' stocks.
    Runs weekly to keep business profiles fresh.
    """
    logger.info("Starting business profile update job")
    start_time = datetime.utcnow()
    
    try:
        from models import db, MarketData
        from handlers.market_data.financial_handler import sync_financials
        from handlers.market_data.forecast_handler import sync_forecast_data
        from handlers.market_data.stock_handler import sync_stock_news
        
        app = get_app()
        with app.app_context():
            # Only update stocks that are approved for the public directory
            listed_stocks = MarketData.query.filter_by(is_listed=True, asset_type='stock').all()
            symbols = [s.symbol for s in listed_stocks]
            
            if not symbols:
                logger.info("No listed stocks to update")
                return {'status': 'ok', 'updated': 0}
            
            success_count = 0
            error_count = 0
            
            for symbol in symbols:
                try:
                    # Sync Financials, Forecasts, and News
                    sync_financials(symbol)
                    sync_forecast_data(symbol)
                    sync_stock_news(symbol)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync profile for {symbol}: {e}")
                    error_count += 1
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Business profile update complete: {success_count} synced, {error_count} errors in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'synced': success_count,
                'errors': error_count,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Business profile update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_financials() -> Dict[str, Any]:
    """
    Update comprehensive financial statements for all listed stocks.
    Syncs both annual and quarterly data.
    Runs weekly (financials don't change frequently).
    """
    logger.info("Starting financials update job")
    start_time = datetime.utcnow()
    
    try:
        from models import db, MarketData
        from handlers.market_data.financial_handler import sync_all_financials
        
        app = get_app()
        with app.app_context():
            # Get all listed stocks
            listed_stocks = MarketData.query.filter_by(is_listed=True, asset_type='stock').all()
            symbols = [s.symbol for s in listed_stocks]
            
            if not symbols:
                logger.info("No listed stocks to update financials")
                return {'status': 'ok', 'updated': 0}
            
            success_count = 0
            error_count = 0
            
            for symbol in symbols:
                try:
                    result = sync_all_financials(symbol)
                    if result.get('status') in ['success', 'partial']:
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync financials for {symbol}: {e}")
                    error_count += 1
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Financials update complete: {success_count} synced, {error_count} errors in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'synced': success_count,
                'errors': error_count,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Financials update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_all_forex() -> Dict[str, Any]:
    """
    Update all forex exchange rates from yfinance.
    """
    logger.info("Starting forex update job")
    start_time = datetime.utcnow()
    
    try:
        from handlers.market_data.forex_handler import import_forex_to_db
        
        app = get_app()
        with app.app_context():
            result = import_forex_to_db()
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Forex update complete: {result.get('updated', 0)} updated in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                **result,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Forex update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_all_forecasts() -> Dict[str, Any]:
    """
    Update analyst forecasts for all listed stocks.
    """
    logger.info("Starting forecasts update job")
    start_time = datetime.utcnow()
    
    try:
        from models import MarketData
        from handlers.market_data.forecast_handler import sync_forecast_data
        
        app = get_app()
        with app.app_context():
            # Original route logic limited to 50, keeping that for now or removing limit? 
            # Route said: stocks = MarketData.query.filter_by(asset_type='stock').limit(50).all()
            # Let's keep consistency but maybe we should update ALL eventually.
            listed_stocks = MarketData.query.filter_by(asset_type='stock').limit(50).all() 
            symbols = [s.symbol for s in listed_stocks]
            
            if not symbols:
                logger.info("No stocks to update forecasts")
                return {'status': 'ok', 'updated': 0}
            
            success_count = 0
            error_count = 0
            
            for symbol in symbols:
                try:
                    result = sync_forecast_data(symbol)
                    if result.get('status') == 'success':
                        success_count += 1
                    else:
                        error_count += 1
                except Exception as e:
                    logger.error(f"Failed to sync forecast for {symbol}: {e}")
                    error_count += 1
            
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"Forecasts update complete: {success_count} synced, {error_count} errors in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'synced': success_count,
                'errors': error_count,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"Forecasts update job failed: {e}")
        return {'status': 'error', 'error': str(e)}


def update_ytd_returns() -> Dict[str, Any]:
    """
    Calculate and update YTD (Year-to-Date) returns for all stocks.
    Runs once a day to keep sector analysis accurate.
    """
    logger.info("Starting YTD returns update job")
    start_time = datetime.utcnow()
    
    try:
        from models import db, MarketData
        import yfinance as yf
        
        app = get_app()
        with app.app_context():
            stocks = MarketData.query.filter_by(asset_type='stock').all()
            
            if not stocks:
                return {'status': 'ok', 'updated': 0}
                
            updated_count = 0
            error_count = 0
            
            for stock in stocks:
                try:
                    # Fetch history from start of year
                    ticker = yf.Ticker(stock.symbol)
                    hist = ticker.history(period="ytd")
                    
                    if not hist.empty and len(hist) > 1:
                        first_price = float(hist['Close'].iloc[0])
                        current_price = float(hist['Close'].iloc[-1])
                        
                        if first_price > 0:
                            ytd_perf = ((current_price - first_price) / first_price) * 100
                            stock.ytd_return = ytd_perf
                            updated_count += 1
                            
                            # Commit in small batches to prevent long locks
                            if updated_count % 10 == 0:
                                db.session.commit()
                except Exception as e:
                    logger.warning(f"Could not calculate YTD for {stock.symbol}: {e}")
                    error_count += 1
            
            db.session.commit()
            elapsed = (datetime.utcnow() - start_time).total_seconds()
            logger.info(f"YTD update complete: {updated_count} updated in {elapsed:.1f}s")
            
            return {
                'status': 'ok',
                'updated': updated_count,
                'errors': error_count,
                'elapsed_seconds': elapsed
            }
    except Exception as e:
        logger.error(f"YTD update job failed: {e}")
        return {'status': 'error', 'error': str(e)}

