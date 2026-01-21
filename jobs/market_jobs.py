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
            symbols = [s.symbol for s in stocks]
            
            if not symbols:
                logger.info("No stocks to update")
                return {'status': 'ok', 'updated': 0}
            
            # Update in batches of 50 to avoid rate limits
            batch_size = 50
            total_updated = 0
            total_errors = 0
            
            for i in range(0, len(symbols), batch_size):
                batch = symbols[i:i + batch_size]
                result = import_stocks_to_db(batch)
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
            result = import_indices_to_db(symbols)
            
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
            result = import_commodities_to_db(symbols)
            
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
                    # Sync both Financials and Forecasts
                    sync_financials(symbol)
                    sync_forecast_data(symbol)
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
