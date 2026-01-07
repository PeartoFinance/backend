"""
Admin Audit Log Routes
GET /api/admin/audit
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from models import db, AuditEvent

audit_bp = Blueprint('admin_audit', __name__)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@audit_bp.route('/audit', methods=['GET'])
@admin_required
def get_audit_events():
    """Get audit events with pagination"""
    try:
        limit = min(200, request.args.get('limit', 50, type=int))
        cursor = request.args.get('cursor')
        
        query = AuditEvent.query.order_by(AuditEvent.ts.desc())
        
        if cursor:
            query = query.filter(AuditEvent.ts < cursor)
        
        events = query.limit(limit).all()
        
        next_cursor = events[-1].ts.isoformat() if events and len(events) == limit else None
        
        return jsonify({
            'events': [{
                'id': e.id,
                'ts': e.ts.isoformat() if e.ts else None,
                'actor': e.actor,
                'action': e.action,
                'entity': e.entity,
                'entityId': e.entityId,
                'meta': e.meta,
            } for e in events],
            'nextCursor': next_cursor
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@audit_bp.route('/audit/stats', methods=['GET'])
@admin_required
def get_audit_stats():
    """Get audit statistics"""
    try:
        total = AuditEvent.query.count()
        
        # Group by action
        from sqlalchemy import func
        action_counts = db.session.query(
            AuditEvent.action, func.count(AuditEvent.id)
        ).group_by(AuditEvent.action).all()
        
        return jsonify({
            'total': total,
            'byAction': {action: count for action, count in action_counts}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
