"""
Admin Pricing Routes
CRUD for Pricing plans
"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Pricing, AuditEvent
from ..decorators import admin_required

pricing_bp = Blueprint('admin_pricing', __name__, url_prefix='/pricing')


def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=str(entity_id),
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


@pricing_bp.route('', methods=['GET'])
@admin_required
def get_pricing_plans():
    """List all pricing plans"""
    try:
        plans = Pricing.query.order_by(Pricing.sort_order.asc()).all()

        return jsonify({
            'plans': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'priceMonthly': float(p.price_monthly) if p.price_monthly else 0,
                'priceYearly': float(p.price_yearly) if p.price_yearly else 0,
                'currency': p.currency,
                'features': p.features,
                'isPopular': p.is_popular,
                'isActive': p.is_active,
                'sortOrder': p.sort_order,
                'createdAt': p.created_at.isoformat() if p.created_at else None,
            } for p in plans],
            'total': len(plans)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pricing_bp.route('/<int:plan_id>', methods=['GET'])
@admin_required
def get_pricing_plan(plan_id):
    """Get single pricing plan"""
    try:
        p = Pricing.query.get_or_404(plan_id)
        return jsonify({
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'priceMonthly': float(p.price_monthly) if p.price_monthly else 0,
            'priceYearly': float(p.price_yearly) if p.price_yearly else 0,
            'currency': p.currency,
            'features': p.features,
            'isPopular': p.is_popular,
            'isActive': p.is_active,
            'sortOrder': p.sort_order,
            'createdAt': p.created_at.isoformat() if p.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@pricing_bp.route('', methods=['POST'])
@admin_required
def create_pricing_plan():
    """Create a new pricing plan"""
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Plan name is required'}), 400

        plan = Pricing(
            name=data['name'],
            description=data.get('description'),
            price_monthly=data.get('priceMonthly', 0),
            price_yearly=data.get('priceYearly', 0),
            currency=data.get('currency', 'USD'),
            features=data.get('features', []),
            is_popular=data.get('isPopular', False),
            is_active=data.get('isActive', True),
            sort_order=data.get('sortOrder', 0),
            created_at=datetime.utcnow()
        )

        db.session.add(plan)
        db.session.commit()

        log_audit('PRICING_CREATE', 'pricing', plan.id, {'name': data['name']})

        return jsonify({'ok': True, 'id': plan.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@pricing_bp.route('/<int:plan_id>', methods=['PUT'])
@admin_required
def update_pricing_plan(plan_id):
    """Update a pricing plan"""
    try:
        plan = Pricing.query.get_or_404(plan_id)
        data = request.get_json()

        if 'name' in data:
            plan.name = data['name']
        if 'description' in data:
            plan.description = data['description']
        if 'priceMonthly' in data:
            plan.price_monthly = data['priceMonthly']
        if 'priceYearly' in data:
            plan.price_yearly = data['priceYearly']
        if 'currency' in data:
            plan.currency = data['currency']
        if 'features' in data:
            plan.features = data['features']
        if 'isPopular' in data:
            plan.is_popular = data['isPopular']
        if 'isActive' in data:
            plan.is_active = data['isActive']
        if 'sortOrder' in data:
            plan.sort_order = data['sortOrder']

        db.session.commit()
        log_audit('PRICING_UPDATE', 'pricing', plan_id, data)

        return jsonify({'ok': True, 'message': 'Pricing plan updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@pricing_bp.route('/<int:plan_id>', methods=['DELETE'])
@admin_required
def delete_pricing_plan(plan_id):
    """Delete a pricing plan"""
    try:
        plan = Pricing.query.get_or_404(plan_id)

        db.session.delete(plan)
        db.session.commit()

        log_audit('PRICING_DELETE', 'pricing', plan_id)

        return jsonify({'ok': True, 'message': 'Pricing plan deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
