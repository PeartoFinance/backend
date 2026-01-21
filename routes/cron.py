"""
Cron URL Routes
External cURL-accessible endpoints for cPanel or external cron services
These endpoints don't start the scheduler but run jobs directly
"""
from flask import Blueprint, jsonify, request
import os

cron_bp = Blueprint('cron', __name__)

# Secret token for cron requests - set in .env
CRON_SECRET = os.getenv('CRON_SECRET', 'your-cron-secret-key')


def verify_cron_token():
    """Verify the cron secret token from request"""
    token = request.headers.get('X-Cron-Token') or request.args.get('token')
    return token == CRON_SECRET


@cron_bp.route('/stocks', methods=['GET', 'POST'])
def cron_update_stocks():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/stocks?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_stocks
        result = update_all_stocks()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/crypto', methods=['GET', 'POST'])
def cron_update_crypto():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/crypto?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_crypto
        result = update_all_crypto()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/indices', methods=['GET', 'POST'])
def cron_update_indices():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/indices?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_indices
        result = update_all_indices()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/commodities', methods=['GET', 'POST'])
def cron_update_commodities():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/commodities?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_all_commodities
        result = update_all_commodities()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/earnings', methods=['GET', 'POST'])
def cron_update_earnings():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/earnings?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_earnings_calendar
        result = update_earnings_calendar()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/dividends', methods=['GET', 'POST'])
def cron_update_dividends():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/dividends?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_dividends
        result = update_dividends()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/watchlist-alerts', methods=['GET', 'POST'])
def cron_check_watchlist():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/watchlist-alerts?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import check_watchlist_alerts
        result = check_watchlist_alerts()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/daily-digest', methods=['GET', 'POST'])
def cron_daily_digest():
    """cURL: curl -X POST http://192.168.1.71:5000/api/cron/daily-digest?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.notification_jobs import send_daily_digest
        result = send_daily_digest()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/all-market', methods=['GET', 'POST'])
def cron_all_market():
    """
    Update all market data at once
    cURL: curl -X POST http://192.168.1.71:5000/api/cron/all-market?token=YOUR_TOKEN
    """
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import (
            update_all_stocks,
            update_all_crypto,
            update_all_indices,
            update_all_commodities,
        )
        
        results = {
            'stocks': update_all_stocks(),
            'crypto': update_all_crypto(),
            'indices': update_all_indices(),
            'commodities': update_all_commodities(),
        }
        return jsonify({'ok': True, 'results': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@cron_bp.route('/business-profiles', methods=['GET', 'POST'])
def cron_update_business_profiles():
    """cURL: curl -X POST http://localhost:5000/api/cron/business-profiles?token=YOUR_TOKEN"""
    if not verify_cron_token():
        return jsonify({'error': 'Invalid cron token'}), 401
    
    try:
        from jobs.market_jobs import update_business_profiles
        result = update_business_profiles()
        return jsonify({'ok': True, **result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
