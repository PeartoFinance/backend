"""
Admin Dashboard Routes
GET /api/admin/stats - Dashboard statistics
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from models import db, User, NewsItem, ToolSettings, Post, Page, Subscriber, AuditEvent

dashboard_bp = Blueprint('admin_dashboard', __name__)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check for admin secret header or session
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        # TODO: Validate against actual admin secret from config
        return f(*args, **kwargs)
    return decorated


@dashboard_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """Get dashboard statistics"""
    try:
        stats = {
            'users': User.query.count(),
            'news': NewsItem.query.count(),
            'tools': ToolSettings.query.filter_by(enabled=True).count(),
            'posts': db.session.query(db.func.count()).select_from(Post).scalar() if db.session.query(Post).first() is not None else 0,
            'pages': db.session.query(db.func.count()).select_from(Page).scalar() if db.session.query(Page).first() is not None else 0,
            'subscribers': Subscriber.query.count() if db.session.query(Subscriber).first() is not None else 0,
        }

        # Get recent audit events
        audit_events = AuditEvent.query.order_by(AuditEvent.ts.desc()).limit(5).all()
        stats['recentActivity'] = [{
            'id': e.id,
            'action': e.action,
            'entity': e.entity,
            'entityId': e.entityId,
            'ts': e.ts.isoformat() if e.ts else None
        } for e in audit_events]

        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
