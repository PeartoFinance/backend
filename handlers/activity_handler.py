"""
Activity Tracking Handler
Centralized activity logging for all user actions across the platform
"""
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from flask import request


def track_activity(
    user_id: int,
    action: str,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[str] = None,
    ip_address: Optional[str] = None,
    extra_data: Optional[Dict[str, Any]] = None
) -> str:
    """
    Track a user activity.
    
    Args:
        user_id: The user ID performing the action
        action: Action type (e.g., 'login', 'document_upload', 'alert_created')
        entity_type: Type of entity (e.g., 'document', 'alert', 'course')
        entity_id: ID of the entity being acted upon
        details: Additional details string
        ip_address: Override IP address (defaults to request IP)
        extra_data: Additional data to append to details
    
    Returns:
        The activity ID
    """
    from models import db, UserActivity
    
    # Build details string
    details_str = details or ''
    if extra_data:
        extra_parts = [f"{k}={v}" for k, v in extra_data.items()]
        if details_str:
            details_str += ';' + ';'.join(extra_parts)
        else:
            details_str = ';'.join(extra_parts)
    
    # Get IP from request if not provided
    if ip_address is None:
        try:
            ip_address = request.remote_addr
        except RuntimeError:
            ip_address = None
    
    activity_id = str(uuid.uuid4())
    
    activity = UserActivity(
        id=activity_id,
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details_str if details_str else None,
        ip_address=ip_address,
        created_at=datetime.now(timezone.utc)
    )
    
    db.session.add(activity)
    db.session.commit()
    
    return activity_id


# ============== CONVENIENCE FUNCTIONS ==============

def track_login(user_id: int, success: bool = True, method: str = 'email', ip: str = None):
    """Track login activity"""
    return track_activity(
        user_id=user_id,
        action='login_success' if success else 'login_failed',
        entity_type='auth',
        extra_data={'method': method},
        ip_address=ip
    )


def track_signup(user_id: int, method: str = 'email', ip: str = None):
    """Track signup activity"""
    return track_activity(
        user_id=user_id,
        action='signup',
        entity_type='auth',
        extra_data={'method': method},
        ip_address=ip
    )


def track_logout(user_id: int, ip: str = None):
    """Track logout activity"""
    return track_activity(
        user_id=user_id,
        action='logout',
        entity_type='auth',
        ip_address=ip
    )


def track_document_upload(user_id: int, doc_id: str, doc_type: str, ip: str = None):
    """Track document upload"""
    return track_activity(
        user_id=user_id,
        action='document_upload',
        entity_type='document',
        entity_id=doc_id,
        extra_data={'document_type': doc_type},
        ip_address=ip
    )


def track_alert_created(user_id: int, alert_id: str, symbol: str, condition: str, target: float, ip: str = None):
    """Track alert creation"""
    return track_activity(
        user_id=user_id,
        action='alert_created',
        entity_type='alert',
        entity_id=alert_id,
        extra_data={'symbol': symbol, 'condition': condition, 'target': target},
        ip_address=ip
    )


def track_alert_triggered(user_id: int, alert_id: str, symbol: str, price: float):
    """Track alert triggered"""
    return track_activity(
        user_id=user_id,
        action='alert_triggered',
        entity_type='alert',
        entity_id=alert_id,
        extra_data={'symbol': symbol, 'price': price}
    )


def track_watchlist_add(user_id: int, symbol: str, ip: str = None):
    """Track watchlist addition"""
    return track_activity(
        user_id=user_id,
        action='watchlist_add',
        entity_type='watchlist',
        entity_id=symbol,
        ip_address=ip
    )


def track_watchlist_remove(user_id: int, symbol: str, ip: str = None):
    """Track watchlist removal"""
    return track_activity(
        user_id=user_id,
        action='watchlist_remove',
        entity_type='watchlist',
        entity_id=symbol,
        ip_address=ip
    )


def track_course_enroll(user_id: int, course_id: int, course_title: str, ip: str = None):
    """Track course enrollment"""
    return track_activity(
        user_id=user_id,
        action='course_enroll',
        entity_type='course',
        entity_id=str(course_id),
        details=course_title,
        ip_address=ip
    )


def track_course_unenroll(user_id: int, course_id: int, ip: str = None):
    """Track course unenrollment"""
    return track_activity(
        user_id=user_id,
        action='course_unenroll',
        entity_type='course',
        entity_id=str(course_id),
        ip_address=ip
    )


def track_module_complete(user_id: int, module_id: int, course_id: int, ip: str = None):
    """Track module completion"""
    return track_activity(
        user_id=user_id,
        action='module_complete',
        entity_type='module',
        entity_id=str(module_id),
        extra_data={'course_id': course_id},
        ip_address=ip
    )


def track_profile_update(user_id: int, fields_changed: list, ip: str = None):
    """Track profile update"""
    return track_activity(
        user_id=user_id,
        action='profile_update',
        entity_type='profile',
        details=','.join(fields_changed) if fields_changed else None,
        ip_address=ip
    )


def track_password_change(user_id: int, ip: str = None):
    """Track password change"""
    return track_activity(
        user_id=user_id,
        action='password_change',
        entity_type='security',
        ip_address=ip
    )


def track_settings_update(user_id: int, setting_type: str, ip: str = None):
    """Track settings update"""
    return track_activity(
        user_id=user_id,
        action='settings_update',
        entity_type='settings',
        entity_id=setting_type,
        ip_address=ip
    )


def track_portfolio_transaction(user_id: int, tx_type: str, symbol: str, quantity: float, price: float, ip: str = None):
    """Track portfolio transaction"""
    return track_activity(
        user_id=user_id,
        action=f'portfolio_{tx_type}',
        entity_type='portfolio',
        entity_id=symbol,
        extra_data={'quantity': quantity, 'price': price},
        ip_address=ip
    )
