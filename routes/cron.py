"""
Cron URL Routes
External cURL-accessible endpoints for cPanel or external cron services
These endpoints don't start the scheduler but run jobs directly or enqueue them
"""
from flask import Blueprint, jsonify, request
import os
from jobs.scheduler import queue_job

cron_bp = Blueprint('cron', __name__)

# Secret token for cron requests - set in .env
CRON_SECRET = os.getenv('CRON_SECRET', 'your-cron-secret-key')


def verify_cron_token():
    """Verify the cron secret token from request"""
    token = request.headers.get('X-Cron-Token') or request.args.get('token')
    return token == CRON_SECRET


@cron_bp.route('/stocks', methods=['GET', 'POST'])
def cron_update_stocks():
    """cURL: curl -X POST https://api.pearto.com/api/cron/stocks?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_stocks
        queue_job(update_all_stocks, 'update_all_stocks')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/crypto', methods=['GET', 'POST'])
def cron_update_crypto():
    """cURL: curl -X POST https://api.pearto.com/api/cron/crypto?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_crypto
        queue_job(update_all_crypto, 'update_all_crypto')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/indices', methods=['GET', 'POST'])
def cron_update_indices():
    """cURL: curl -X POST https://api.pearto.com/api/cron/indices?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_indices
        queue_job(update_all_indices, 'update_all_indices')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/commodities', methods=['GET', 'POST'])
def cron_update_commodities():
    """cURL: curl -X POST https://api.pearto.com/api/cron/commodities?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_commodities
        queue_job(update_all_commodities, 'update_all_commodities')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/earnings', methods=['GET', 'POST'])
def cron_update_earnings():
    """cURL: curl -X POST https://api.pearto.com/api/cron/earnings?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_earnings_calendar
        queue_job(update_earnings_calendar, 'update_earnings_calendar')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/dividends', methods=['GET', 'POST'])
def cron_update_dividends():
    """cURL: curl -X POST https://api.pearto.com/api/cron/dividends?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_dividends
        queue_job(update_dividends, 'update_dividends')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/watchlist-alerts', methods=['GET', 'POST'])
def cron_check_watchlist():
    """cURL: curl -X POST https://api.pearto.com/api/cron/watchlist-alerts?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import check_watchlist_alerts
        queue_job(check_watchlist_alerts, 'check_watchlist_alerts')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/earnings-alerts', methods=['GET', 'POST'])
def cron_check_earnings():
    """
    cPanel Cron: URL-accessible endpoint for earnings alerts.
    Checks both user watchlists and their actual portfolio holdings.
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import check_earnings_alerts
        queue_job(check_earnings_alerts, 'check_earnings_alerts')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@cron_bp.route('/portfolio-summary', methods=['GET', 'POST'])
def cron_daily_pl_summary():
    """
    cPanel Cron: URL-accessible endpoint for daily P&L summaries.
    Compares latest WealthState snapshots to determine gain/loss.
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import send_daily_pl_summaries
        queue_job(send_daily_pl_summaries, 'send_daily_pl_summaries')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/daily-digest', methods=['GET', 'POST'])
def cron_daily_digest():
    """cURL: curl -X POST https://api.pearto.com/api/cron/daily-digest?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import send_daily_digest
        queue_job(send_daily_digest, 'send_daily_digest')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/all-market', methods=['GET', 'POST'])
def cron_all_market():
    """
    Update all market data at once
    cURL: curl -X POST https://api.pearto.com/api/cron/all-market?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import (
            update_all_stocks,
            update_all_crypto,
            update_all_indices,
            update_all_commodities,
            update_business_profiles,
            update_all_forex,
        )
        
        # Enqueue individual jobs so they run sequentially in the worker
        queue_job(update_all_stocks, 'update_all_stocks')
        queue_job(update_all_crypto, 'update_all_crypto')
        queue_job(update_all_indices, 'update_all_indices')
        queue_job(update_all_commodities, 'update_all_commodities')
        queue_job(update_business_profiles, 'update_business_profiles')
        queue_job(update_all_forex, 'update_all_forex')
        
        return jsonify({'ok': True, 'message': 'All market jobs triggered/queued'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/business-profiles', methods=['GET', 'POST'])
def cron_update_business_profiles():
    """cURL: curl -X POST https://api.pearto.com/api/cron/business-profiles?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_business_profiles
        queue_job(update_business_profiles, 'update_business_profiles')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/cleanup-accounts', methods=['GET', 'POST'])
def cron_cleanup_accounts():
    """
    Permanently delete accounts marked for deletion > 30 days ago.
    cURL: curl -X POST https://api.pearto.com/api/cron/cleanup-accounts?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401

    try:
        from jobs.system_jobs import cleanup_deleted_accounts
        queue_job(cleanup_deleted_accounts, 'cleanup_deleted_accounts')
        return jsonify({'ok': True, 'message': 'Cleanup triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/financials', methods=['GET', 'POST'])
def cron_update_financials():
    """
    Sync financial statements for all listed stocks.
    cURL: curl -X POST https://api.pearto.com/api/cron/financials?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401

    try:
        from jobs.market_jobs import update_financials
        queue_job(update_financials, 'update_financials')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/forecast', methods=['GET', 'POST'])
def cron_update_forecast():
    """
    Sync analyst forecast data. This one is tricky because it takes params.
    TODO: Support params in CronJob model if needed. For now, running directly for parameterized calls?
    Wait, the user wants ALL jobs wrapped. But parameterized calls are usually one-off.
    Let's run it directly if it has params, but bulk updates can be queued.
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401

    try:
        from handlers.market_data.forecast_handler import sync_forecast_data
        from models.market import MarketData

        symbol = request.args.get('symbol')
        if symbol:
            # Interactive: Enqueue specific symbol update for faster response (but still async)
            # OR run effectively immediately if user expects result.
            # User wants "cron scheduler system", which implies queuing.
            # But returning result immediately is nice. 
            # However, to be consistent with "all api cron routes use cron jobs scheduling", 
            # we should queue it.
            # But wait, the route returns "result". Queuing returns "queued".
            # The user provided checking link for "all-market".
            # Let's queue it to be safe.
            queue_job(sync_forecast_data, 'sync_forecast_data', symbol.upper())
            return jsonify({'ok': True, 'symbol': symbol, 'message': 'Job triggered'})

        # Bulk update - Queue it!
        from jobs.market_jobs import update_all_forecasts
        queue_job(update_all_forecasts, 'update_all_forecasts')

        return jsonify({'ok': True, 'message': 'Forecast update job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/import-news', methods=['GET', 'POST'])
def cron_import_news():
    """
    Import news from all external sources.
    cURL: curl -X POST https://api.pearto.com/api/cron/import-news?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401

    try:
        from jobs.news_jobs import import_all_news
        queue_job(import_all_news, 'import_all_news')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/import-stock-profiles', methods=['GET', 'POST'])
def cron_import_stock_profiles():
    """
    Alias for /stocks - Updates stock profiles/prices.
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
        
    try:
        from jobs.market_jobs import update_all_stocks
        queue_job(update_all_stocks, 'update_all_stocks')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/import-business-profiles', methods=['GET', 'POST'])
def cron_import_biz_profiles():
    """
    Alias for /business-profiles - Updates financials, forecasts, and company news.
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
        
    try:
        from jobs.market_jobs import update_business_profiles
        queue_job(update_business_profiles, 'update_business_profiles')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== NEWS FETCHING ====================
@cron_bp.route('/news-notifications', methods=['GET', 'POST'])
def cron_news_notifications():
    """
    Fetch recent news and send notifications to users based on preferences.
    cURL: curl -X POST https://api.pearto.com/api/cron/news-notifications?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import process_news_notifications
        queue_job(process_news_notifications, 'process_news_notifications')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e), 'ok': False}), 500


@cron_bp.route('/forex', methods=['GET', 'POST'])
def cron_update_forex():
    """cURL: curl -X POST https://api.pearto.com/api/cron/forex?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_forex
        queue_job(update_all_forex, 'update_all_forex')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/wealth-snapshot', methods=['GET', 'POST'])
def cron_wealth_snapshot():
    """
    Manually trigger a wealth snapshot for all users.
    cURL: curl -X POST https://api.pearto.com/api/cron/wealth-snapshot?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.system_jobs import snapshot_user_wealth
        queue_job(snapshot_user_wealth, 'snapshot_user_wealth')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/check-goals', methods=['GET', 'POST'])
def cron_check_goals():
    """
    cPanel Cron: URL-accessible endpoint to check user financial goals.
    cURL example: curl -X POST https://api.pearto.com/api/cron/check-goals?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import check_financial_goals
        queue_job(check_financial_goals, 'check_financial_goals')
        return jsonify({'ok': True, 'message': 'Job triggered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500