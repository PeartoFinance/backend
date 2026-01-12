"""
Admin Dashboard Routes
GET /api/admin/stats - Dashboard statistics
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required
from models import db, User, NewsItem, ToolSettings, Post, Page, Subscriber, AuditEvent

dashboard_bp = Blueprint('admin_dashboard', __name__)


@dashboard_bp.route('/stats', methods=['GET'])
@admin_required
def get_stats():
    """Get dashboard statistics"""
    try:
        country = getattr(request, 'user_country', 'US')
        stats = {
            'users': User.query.filter((User.country_code == country) | (User.country_code == 'GLOBAL')).count(),
            'news': NewsItem.query.filter((NewsItem.country_code == country) | (NewsItem.country_code == 'GLOBAL')).count(),
            'tools': ToolSettings.query.filter((ToolSettings.country_code == country) | (ToolSettings.country_code == 'GLOBAL')).filter_by(enabled=True).count(),
            'posts': Post.query.filter((Post.country_code == country) | (Post.country_code == 'GLOBAL')).count(),
            'pages': Page.query.filter((Page.country_code == country) | (Page.country_code == 'GLOBAL')).count(),
            'subscribers': Subscriber.query.filter((Subscriber.country_code == country) | (Subscriber.country_code == 'GLOBAL')).count(),
        }

        # Get recent audit events
        audit_events = AuditEvent.query.filter(
            (AuditEvent.country_code == country) | (AuditEvent.country_code == 'GLOBAL')
        ).order_by(AuditEvent.ts.desc()).limit(5).all()
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
