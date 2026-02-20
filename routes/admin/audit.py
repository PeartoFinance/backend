"""
Admin Audit Log Routes
GET /api/admin/audit
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required
from models import db, AuditEvent

audit_bp = Blueprint('admin_audit', __name__)


@audit_bp.route('/audit', methods=['GET'])
@admin_required
def get_audit_events():
    """Get audit events with pagination"""
    try:
        limit = min(200, request.args.get('limit', 50, type=int))
        cursor = request.args.get('cursor')
        country = getattr(request, 'user_country', 'US')
        is_global = not country or country == 'GLOBAL'
        
        query = AuditEvent.query
        if not is_global:
            query = query.filter(
                (AuditEvent.country_code == country) | (AuditEvent.country_code == 'GLOBAL')
            )
        
        query = query.order_by(AuditEvent.ts.desc())
        
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
        country = getattr(request, 'user_country', 'US')
        is_global = not country or country == 'GLOBAL'

        query = AuditEvent.query
        if not is_global:
            query = query.filter(
                (AuditEvent.country_code == country) | (AuditEvent.country_code == 'GLOBAL')
            )
            
        total = query.count()
        
        # Group by action
        from sqlalchemy import func
        stats_query = db.session.query(
            AuditEvent.action, func.count(AuditEvent.id)
        )
        if not is_global:
            stats_query = stats_query.filter(
                (AuditEvent.country_code == country) | (AuditEvent.country_code == 'GLOBAL')
            )
        action_counts = stats_query.group_by(AuditEvent.action).all()
        
        return jsonify({
            'total': total,
            'byAction': {action: count for action, count in action_counts}
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
