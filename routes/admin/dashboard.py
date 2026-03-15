"""
Admin Dashboard Routes
GET /api/admin/stats - Dashboard statistics
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, User, NewsItem, ToolSettings, Post, Page, Subscriber, AuditEvent

dashboard_bp = Blueprint('admin_dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@permission_required("dashboard")
def get_stats():
    """Get dashboard statistics"""
    try:
        country = getattr(request, 'user_country', 'US')
        
        # Determine if we should apply country filtering.
        # If country is 'GLOBAL', None, or empty, we treat it as "All Countries" and show everything.
        is_global = not country or country == 'GLOBAL'
        
        def apply_country_filter(query, model):
            if is_global:
                return query
            return query.filter((model.country_code == country) | (model.country_code == 'GLOBAL'))

        stats = {
            'users': apply_country_filter(User.query, User).count(),
            'news': apply_country_filter(NewsItem.query, NewsItem).count(),
            'tools': apply_country_filter(ToolSettings.query, ToolSettings).filter_by(enabled=True).count(),
            'posts': apply_country_filter(Post.query, Post).count(),
            'pages': apply_country_filter(Page.query, Page).count(),
            'subscribers': apply_country_filter(Subscriber.query, Subscriber).count(),
        }

        # Get recent audit events
        audit_query = AuditEvent.query
        if not is_global:
            audit_query = audit_query.filter(
                (AuditEvent.country_code == country) | (AuditEvent.country_code == 'GLOBAL')
            )
            
        audit_events = audit_query.order_by(AuditEvent.ts.desc()).limit(5).all()
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
