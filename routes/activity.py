"""
Activity Tracking API Routes
- Page view tracking for analytics
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from models import db, User, UserActivity
from .decorators import auth_required


activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/activity/page-view', methods=['POST'])
@auth_required
def track_page_view():
    """
    Track a page view event.

    Expected JSON:
    {
        "path": "/some/path",
        "title": "Optional page title",
        "referrer": "Optional referrer"
    }
    """
    user = request.user
    data = request.get_json() or {}
    path = data.get('path') or request.path
    title = data.get('title')
    referrer = data.get('referrer')

    activity = UserActivity(
        id=str(uuid.uuid4()),
        user_id=user.id,
        action='page_view',
        entity_type='page',
        entity_id=path,
        details=f"title={title or ''};referrer={referrer or ''}",
        ip_address=request.remote_addr,
        created_at=datetime.utcnow(),
    )
    db.session.add(activity)
    db.session.commit()

    return jsonify({'success': True}), 201
