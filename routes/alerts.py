"""
User Alerts API Routes
CRUD for user price/event alerts
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
from routes.decorators import auth_required
from models import db, UserAlert

alerts_bp = Blueprint('alerts', __name__)


@alerts_bp.route('', methods=['GET'])
@auth_required
def get_alerts():
    """Get all user alerts"""
    alerts = UserAlert.query.filter_by(user_id=request.user.id).order_by(UserAlert.created_at.desc()).all()
    
    return jsonify([{
        'id': a.id,
        'symbol': a.symbol,
        'alertType': a.alert_type,
        'condition': a.condition,
        'targetValue': float(a.target_value) if a.target_value else None,
        'isActive': a.is_active,
        'isTriggered': a.is_triggered,
        'triggeredAt': a.triggered_at.isoformat() if a.triggered_at else None,
        'notifyEmail': a.notify_email,
        'notifyPush': a.notify_push,
        'createdAt': a.created_at.isoformat() if a.created_at else None
    } for a in alerts])


@alerts_bp.route('', methods=['POST'])
@auth_required
def create_alert():
    """Create a new alert"""
    data = request.get_json()
    
    symbol = data.get('symbol', '').strip().upper()
    alert_type = data.get('alertType', 'price')
    condition = data.get('condition', 'above')  # above, below, equals
    target_value = data.get('targetValue')
    
    if not symbol or target_value is None:
        return jsonify({'error': 'Symbol and target value required'}), 400
    
    alert = UserAlert(
        id=str(uuid.uuid4()),
        user_id=request.user.id,
        symbol=symbol,
        alert_type=alert_type,
        condition=condition,
        target_value=target_value,
        is_active=True,
        notify_email=data.get('notifyEmail', True),
        notify_push=data.get('notifyPush', True)
    )
    
    db.session.add(alert)
    db.session.commit()
    
    return jsonify({
        'id': alert.id,
        'message': f'Alert created for {symbol}'
    }), 201


@alerts_bp.route('/<alert_id>', methods=['PUT'])
@auth_required
def update_alert(alert_id):
    """Update an alert"""
    alert = UserAlert.query.filter_by(id=alert_id, user_id=request.user.id).first()
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    data = request.get_json()
    
    if 'isActive' in data:
        alert.is_active = data['isActive']
    if 'targetValue' in data:
        alert.target_value = data['targetValue']
    if 'condition' in data:
        alert.condition = data['condition']
    if 'notifyEmail' in data:
        alert.notify_email = data['notifyEmail']
    if 'notifyPush' in data:
        alert.notify_push = data['notifyPush']
    
    db.session.commit()
    
    return jsonify({'message': 'Alert updated'})


@alerts_bp.route('/<alert_id>', methods=['DELETE'])
@auth_required
def delete_alert(alert_id):
    """Delete an alert"""
    alert = UserAlert.query.filter_by(id=alert_id, user_id=request.user.id).first()
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    db.session.delete(alert)
    db.session.commit()
    
    return jsonify({'message': 'Alert deleted'})


@alerts_bp.route('/<alert_id>/toggle', methods=['POST'])
@auth_required
def toggle_alert(alert_id):
    """Toggle alert active status"""
    alert = UserAlert.query.filter_by(id=alert_id, user_id=request.user.id).first()
    if not alert:
        return jsonify({'error': 'Alert not found'}), 404
    
    alert.is_active = not alert.is_active
    db.session.commit()
    
    return jsonify({
        'isActive': alert.is_active,
        'message': f'Alert {"enabled" if alert.is_active else "disabled"}'
    })
