"""
Activity Tracking API Routes
- Page view tracking for analytics
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from models import db, User, UserActivity


activity_bp = Blueprint('activity', __name__)


def get_current_user():
    """Helper to get current user from email header."""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return None
    return User.query.filter_by(email=user_email).first()


@activity_bp.route('/activity/page-view', methods=['POST'])
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
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

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


