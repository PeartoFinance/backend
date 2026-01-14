"""
Jobs Admin API Routes
Manage background jobs via admin panel
"""
from flask import Blueprint, jsonify, request
from routes.decorators import admin_required

jobs_bp = Blueprint('jobs', __name__)


@jobs_bp.route('/status', methods=['GET'])
@admin_required
def get_jobs_status():
    """Get status of all scheduled jobs"""
    try:
        from jobs.scheduler import get_job_status
        return jsonify(get_job_status())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/run/<job_id>', methods=['POST'])
@admin_required
def run_job(job_id):
    """Manually trigger a specific job to run immediately"""
    try:
        from jobs.scheduler import run_job_now
        
        success = run_job_now(job_id)
        if success:
            return jsonify({'ok': True, 'message': f'Job {job_id} triggered'})
        return jsonify({'error': 'Job not found or scheduler not running'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/pause/<job_id>', methods=['POST'])
@admin_required
def pause_job(job_id):
    """Pause a scheduled job"""
    try:
        from jobs.scheduler import pause_job as do_pause
        
        success = do_pause(job_id)
        if success:
            return jsonify({'ok': True, 'message': f'Job {job_id} paused'})
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/resume/<job_id>', methods=['POST'])
@admin_required
def resume_job(job_id):
    """Resume a paused job"""
    try:
        from jobs.scheduler import resume_job as do_resume
        
        success = do_resume(job_id)
        if success:
            return jsonify({'ok': True, 'message': f'Job {job_id} resumed'})
        return jsonify({'error': 'Job not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/run/market/all', methods=['POST'])
@admin_required
def run_all_market_jobs():
    """Run all market data update jobs immediately"""
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


@jobs_bp.route('/run/notifications/watchlist', methods=['POST'])
@admin_required
def run_watchlist_check():
    """Run watchlist alert check immediately"""
    try:
        from jobs.notification_jobs import check_watchlist_alerts
        result = check_watchlist_alerts()
        return jsonify({'ok': True, 'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/config', methods=['GET'])
@admin_required
def get_job_config():
    """Get current job configuration"""
    try:
        from jobs.scheduler import JOB_CONFIG
        return jsonify({'config': JOB_CONFIG})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
