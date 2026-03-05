"""
Activity Tracking API Routes
- Page view tracking for analytics
- User activity log
- Login history
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from sqlalchemy import desc
import uuid
from models import db, User, UserActivity, LoginEvent
from .decorators import auth_required


activity_bp = Blueprint('activity', __name__)


@activity_bp.route('/activity/page-view', methods=['POST'])
@auth_required
def track_page_view():
    """Track a page view event."""
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


@activity_bp.route('/activity', methods=['GET'])
@auth_required
def get_activity():
    """Get user activity log"""
    from utils.validators import safe_pagination
    
    limit, offset = safe_pagination(
        request.args.get('limit'),
        request.args.get('offset'),
        max_limit=100,
        max_offset=5000
    )
    
    activities = UserActivity.query.filter_by(
        user_id=request.user.id
    ).order_by(desc(UserActivity.created_at)).offset(offset).limit(limit).all()
    
    return jsonify([{
        'id': a.id,
        'action': a.action,
        'entityType': a.entity_type,
        'entityId': a.entity_id,
        'details': a.details,
        'ipAddress': a.ip_address,
        'createdAt': a.created_at.isoformat() if a.created_at else None
    } for a in activities])


@activity_bp.route('/activity/logins', methods=['GET'])
@auth_required
def get_login_history():
    """Get user login history"""
    limit = request.args.get('limit', 20, type=int)
    
    logins = LoginEvent.query.filter_by(
        user_id=request.user.id
    ).order_by(desc(LoginEvent.created_at)).limit(limit).all()
    
    return jsonify([{
        'id': l.id,
        'eventType': l.event_type,
        'ipAddress': l.ip_address,
        'userAgent': l.user_agent,
        'location': l.location,
        'success': l.success,
        'failureReason': l.failure_reason,
        'createdAt': l.created_at.isoformat() if l.created_at else None
    } for l in logins])


@activity_bp.route('/activity/summary', methods=['GET'])
@auth_required
def get_activity_summary():
    """Get activity summary stats"""
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    total_activities = UserActivity.query.filter_by(user_id=request.user.id).count()
    recent_activities = UserActivity.query.filter(
        UserActivity.user_id == request.user.id,
        UserActivity.created_at >= week_ago
    ).count()
    
    recent_logins = LoginEvent.query.filter(
        LoginEvent.user_id == request.user.id,
        LoginEvent.created_at >= week_ago,
        LoginEvent.success == True
    ).count()
    
    failed_logins = LoginEvent.query.filter(
        LoginEvent.user_id == request.user.id,
        LoginEvent.created_at >= week_ago,
        LoginEvent.success == False
    ).count()
    
    return jsonify({
        'totalActivities': total_activities,
        'recentActivities': recent_activities,
        'recentLogins': recent_logins,
        'failedLogins': failed_logins
    })

