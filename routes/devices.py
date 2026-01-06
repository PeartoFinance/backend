"""
Device & Session Management API Routes
- Session tracking, device management, logout from devices
Based on old/Frontend/server/src/deviceApi.js
"""
from flask import Blueprint, request, jsonify
import uuid
import re
from datetime import datetime, timedelta
from models import db, User, UserSession

devices_bp = Blueprint('devices', __name__)


def parse_user_agent(user_agent):
    """Parse user agent string for device info"""
    ua = user_agent or ''
    
    # Detect browser
    browser = 'Unknown'
    if 'Chrome' in ua and 'Edge' not in ua:
        browser = 'Chrome'
    elif 'Firefox' in ua:
        browser = 'Firefox'
    elif 'Safari' in ua and 'Chrome' not in ua:
        browser = 'Safari'
    elif 'Edge' in ua:
        browser = 'Edge'
    elif 'Opera' in ua:
        browser = 'Opera'
    
    # Detect OS
    os = 'Unknown'
    if 'Windows' in ua:
        os = 'Windows'
    elif 'Mac OS' in ua:
        os = 'macOS'
    elif 'Linux' in ua and 'Android' not in ua:
        os = 'Linux'
    elif 'Android' in ua:
        os = 'Android'
    elif 'iOS' in ua or 'iPhone' in ua or 'iPad' in ua:
        os = 'iOS'
    
    # Detect device type
    device_type = 'desktop'
    if 'Mobile' in ua:
        device_type = 'mobile'
    elif 'Tablet' in ua or 'iPad' in ua:
        device_type = 'tablet'
    
    return {
        'browser': browser,
        'os': os,
        'device_type': device_type
    }


def get_current_user():
    """Helper to get current user from email header"""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return None
    return User.query.filter_by(email=user_email).first()


def get_client_ip():
    """Get client IP address"""
    return (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip() or
        request.headers.get('X-Real-IP') or
        request.remote_addr or
        'unknown'
    )


@devices_bp.route('/', methods=['GET'])
def get_devices():
    """Get all active sessions for the current user"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get current session token from headers
    current_token = request.headers.get('X-Session-Token', '')
    
    # Get all active sessions (not expired)
    sessions = UserSession.query.filter(
        UserSession.user_id == user.id,
        (UserSession.expires_at == None) | (UserSession.expires_at > datetime.utcnow())
    ).order_by(UserSession.last_activity.desc()).all()
    
    result = []
    for session in sessions:
        result.append({
            'id': session.id,
            'deviceName': getattr(session, 'device_name', f'{session.user_agent[:50]}...' if session.user_agent else 'Unknown'),
            'deviceType': getattr(session, 'device_type', 'desktop'),
            'ipAddress': session.ip_address,
            'lastActivity': session.last_activity.isoformat() if session.last_activity else None,
            'createdAt': session.created_at.isoformat() if session.created_at else None,
            'expiresAt': session.expires_at.isoformat() if session.expires_at else None,
            'isCurrent': session.token == current_token
        })
    
    return jsonify({'sessions': result})


@devices_bp.route('/track', methods=['POST'])
def track_device():
    """Track/create a new session (called on login or app start)"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Parse device info
    user_agent = request.headers.get('User-Agent', '')
    device_info = parse_user_agent(user_agent)
    
    # Get IP
    ip_address = get_client_ip()
    
    # Generate session token
    session_token = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    
    # Device name from request or generate
    data = request.get_json() or {}
    device_name = data.get('deviceName') or f"{device_info['os']} - {device_info['browser']}"
    
    # Session expiry (30 days)
    expires_at = datetime.utcnow() + timedelta(days=30)
    
    # Create new session
    session = UserSession(
        id=session_id,
        user_id=user.id,
        token=session_token,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=expires_at,
        last_activity=datetime.utcnow()
    )
    
    db.session.add(session)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'sessionToken': session_token,
        'sessionId': session_id,
        'message': 'Session tracked successfully'
    })


@devices_bp.route('/<session_id>', methods=['DELETE'])
def revoke_session(session_id):
    """Revoke a specific session"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Delete the session
    result = UserSession.query.filter_by(
        id=session_id,
        user_id=user.id
    ).delete()
    
    if result == 0:
        return jsonify({'error': 'Session not found'}), 404
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Session revoked successfully'
    })


@devices_bp.route('/all/except-current', methods=['DELETE'])
def revoke_all_except_current():
    """Revoke all sessions except the current one"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get current session token
    current_token = request.headers.get('X-Session-Token', '')
    
    # Delete all sessions except current
    result = UserSession.query.filter(
        UserSession.user_id == user.id,
        UserSession.token != current_token
    ).delete()
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'revokedCount': result,
        'message': f'Revoked {result} session(s)'
    })


@devices_bp.route('/<session_id>/rename', methods=['PATCH'])
def rename_device(session_id):
    """Rename a device"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    device_name = data.get('deviceName')
    
    if not device_name or not isinstance(device_name, str):
        return jsonify({'error': 'Device name required'}), 400
    
    # Find and update session
    session = UserSession.query.filter_by(
        id=session_id,
        user_id=user.id
    ).first()
    
    if not session:
        return jsonify({'error': 'Session not found'}), 404
    
    # Note: UserSession model may need device_name column
    # For now, store in user_agent as fallback
    session.user_agent = f'{device_name} | {session.user_agent}'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Device renamed successfully'
    })
