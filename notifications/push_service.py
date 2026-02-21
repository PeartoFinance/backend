"""
OneSignal Push Notification Service
Handles mobile and web push notifications
"""
import os
import logging
from typing import Dict, List, Optional, Any
import requests

from services.settings_service import get_setting_secure

logger = logging.getLogger(__name__)

# OneSignal Configuration Helpers
def get_onesignal_app_id():
    return get_setting_secure('ONESIGNAL_APP_ID', '')

def get_onesignal_api_key():
    return get_setting_secure('ONESIGNAL_API_KEY', '')

ONESIGNAL_API_URL = 'https://onesignal.com/api/v1'


def send_push_notification(
    user_id: int,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send push notification to a specific user.
    
    Args:
        user_id: The user's ID in our database
        title: Notification title
        message: Notification body
        data: Additional data payload
        url: URL to open when notification is clicked
    
    Returns:
        API response dict
    """
    app_id = get_onesignal_app_id()
    api_key = get_onesignal_api_key()
    
    if not app_id or not api_key:
        logger.warning("OneSignal not configured, skipping push notification")
        return {'status': 'skipped', 'reason': 'not_configured'}
    
    try:
        from models import UserDevice
        
        # Get user's registered devices
        devices = UserDevice.query.filter_by(
            user_id=user_id,
            is_active=True
        ).all()
        
        if not devices:
            logger.debug(f"No devices registered for user {user_id}")
            return {'status': 'skipped', 'reason': 'no_devices'}
        
        player_ids = [d.device_token for d in devices if d.device_token]
        
        if not player_ids:
            return {'status': 'skipped', 'reason': 'no_tokens'}
        
        return send_bulk_push(
            player_ids=player_ids,
            title=title,
            message=message,
            data=data,
            url=url
        )
    except Exception as e:
        logger.error(f"Push notification failed: {e}")
        return {'status': 'error', 'error': str(e)}


def send_bulk_push(
    player_ids: List[str],
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None,
    url: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send push notification to multiple devices.
    
    Args:
        player_ids: List of OneSignal player IDs
        title: Notification title  
        message: Notification body
        data: Additional data payload
        url: URL to open when clicked
    
    Returns:
        API response dict
    """
    app_id = get_onesignal_app_id()
    api_key = get_onesignal_api_key()
    
    if not app_id or not api_key:
        logger.warning("OneSignal not configured")
        return {'status': 'skipped', 'reason': 'not_configured'}
    
    headers = {
        'Authorization': f'Basic {api_key}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'app_id': app_id,
        'include_player_ids': player_ids,
        'headings': {'en': title},
        'contents': {'en': message},
    }
    
    if data:
        payload['data'] = data
    
    if url:
        payload['url'] = url
    
    try:
        response = requests.post(
            f'{ONESIGNAL_API_URL}/notifications',
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        result = response.json()
        logger.info(f"Push notification sent to {len(player_ids)} devices")
        return {'status': 'sent', 'response': result}
    except requests.exceptions.RequestException as e:
        logger.error(f"OneSignal API error: {e}")
        return {'status': 'error', 'error': str(e)}


def register_device(
    user_id: int,
    player_id: str,
    platform: str = 'web',
    device_name: Optional[str] = None
) -> bool:
    """
    Register a device for push notifications.
    
    Args:
        user_id: User's database ID
        player_id: OneSignal player ID
        platform: Device platform (web, ios, android)
        device_name: Optional device name
    
    Returns:
        True if registration successful
    """
    try:
        from models import db, UserDevice
        from datetime import datetime
        import uuid
        
        # Check if device already registered
        existing = UserDevice.query.filter_by(
            user_id=user_id,
            device_token=player_id
        ).first()
        
        if existing:
            existing.is_active = True
            existing.last_used_at = datetime.utcnow()
            db.session.commit()
            return True
        
        # Create new device registration
        device = UserDevice(
            id=str(uuid.uuid4()),
            user_id=user_id,
            device_name=device_name or f'{platform} device',
            device_type=platform,
            device_token=player_id,
            platform=platform,
            is_active=True,
            last_used_at=datetime.utcnow()
        )
        db.session.add(device)
        db.session.commit()
        
        logger.info(f"Registered device for user {user_id}: {platform}")
        return True
    except Exception as e:
        logger.error(f"Device registration failed: {e}")
        return False


def unregister_device(user_id: int, player_id: str) -> bool:
    """
    Unregister a device from push notifications.
    """
    try:
        from models import db, UserDevice
        
        device = UserDevice.query.filter_by(
            user_id=user_id,
            device_token=player_id
        ).first()
        
        if device:
            device.is_active = False
            db.session.commit()
            return True
        return False
    except Exception as e:
        logger.error(f"Device unregistration failed: {e}")
        return False


def send_topic_notification(
    topic: str,
    title: str,
    message: str,
    data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send notification to all users subscribed to a topic.
    Topics: 'market_alerts', 'news', 'earnings', 'dividends'
    """
    app_id = get_onesignal_app_id()
    api_key = get_onesignal_api_key()
    
    if not app_id or not api_key:
        return {'status': 'skipped', 'reason': 'not_configured'}
    
    headers = {
        'Authorization': f'Basic {api_key}',
        'Content-Type': 'application/json',
    }
    
    payload = {
        'app_id': app_id,
        'included_segments': [topic],
        'headings': {'en': title},
        'contents': {'en': message},
    }
    
    if data:
        payload['data'] = data
    
    try:
        response = requests.post(
            f'{ONESIGNAL_API_URL}/notifications',
            json=payload,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        return {'status': 'sent', 'response': response.json()}
    except requests.exceptions.RequestException as e:
        logger.error(f"Topic notification failed: {e}")
        return {'status': 'error', 'error': str(e)}
