"""
Admin Marketing Routes - Subscribers, Affiliates, Campaigns
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, Subscriber, Affiliate, MarketingCampaign
import uuid
from datetime import datetime

marketing_bp = Blueprint('admin_marketing', __name__)


# ============================================================================
# SUBSCRIBERS
# ============================================================================

@marketing_bp.route('/subscribers', methods=['GET'])
@permission_required("marketing")
def get_subscribers():
    """List all subscribers (country-filtered)"""
    try:
        country = getattr(request, 'user_country', 'US')
        subs = Subscriber.query.filter(
            (Subscriber.country_code == country) | 
            (Subscriber.country_code == 'GLOBAL')
        ).order_by(Subscriber.subscribed_at.desc()).limit(500).all()
        return jsonify({
            'subscribers': [{
                'id': s.id,
                'email': s.email,
                'name': s.name,
                'is_verified': s.is_verified,
                'is_active': s.is_active,
                'source': s.source,
                'country_code': s.country_code,
                'subscribed_at': s.subscribed_at.isoformat() if s.subscribed_at else None
            } for s in subs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/subscribers', methods=['POST'])
@permission_required("marketing")
def create_subscriber():
    """Create a subscriber"""
    try:
        data = request.get_json()
        sub = Subscriber(
            email=data['email'],
            name=data.get('name'),
            is_verified=data.get('is_verified', False),
            is_active=data.get('is_active', True),
            source=data.get('source', 'admin'),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(sub)
        db.session.commit()
        return jsonify({'ok': True, 'id': sub.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/subscribers/<int:id>', methods=['PUT', 'PATCH'])
@permission_required("marketing")
def update_subscriber(id):
    """Update a subscriber"""
    try:
        sub = Subscriber.query.get_or_404(id)
        data = request.get_json()
        if 'name' in data:
            sub.name = data['name']
        if 'is_active' in data:
            sub.is_active = data['is_active']
        if 'is_verified' in data:
            sub.is_verified = data['is_verified']
        if 'country_code' in data:
            sub.country_code = data['country_code']
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/subscribers/<int:id>', methods=['DELETE'])
@permission_required("marketing")
def delete_subscriber(id):
    """Delete a subscriber"""
    try:
        sub = Subscriber.query.get_or_404(id)
        db.session.delete(sub)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# AFFILIATES
# ============================================================================

@marketing_bp.route('/affiliates', methods=['GET'])
@permission_required("marketing")
def get_affiliates():
    """List all affiliates (country-filtered)"""
    try:
        country = getattr(request, 'user_country', 'US')
        affs = Affiliate.query.filter(
            (Affiliate.country_code == country) | 
            (Affiliate.country_code == 'GLOBAL')
        ).all()
        return jsonify({
            'affiliates': [{
                'id': a.id,
                'providerId': a.providerId,
                'category': a.category,
                'affiliateUrl': a.affiliateUrl,
                'linkName': a.linkName,
                'priority': a.priority,
                'active': bool(a.active),
                'country_code': a.country_code
            } for a in affs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/affiliates', methods=['POST'])
@permission_required("marketing")
def create_affiliate():
    """Create an affiliate"""
    try:
        data = request.get_json()
        aff = Affiliate(
            id=str(uuid.uuid4()),
            providerId=data['providerId'],
            category=data['category'],
            affiliateUrl=data['affiliateUrl'],
            linkName=data.get('linkName'),
            priority=data.get('priority', 0),
            active=1 if data.get('active', True) else 0,
            country_code=data.get('country_code', getattr(request, 'user_country', 'US')),
            updatedAt=datetime.utcnow().isoformat()
        )
        db.session.add(aff)
        db.session.commit()
        return jsonify({'ok': True, 'id': aff.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/affiliates/<id>', methods=['PUT', 'PATCH'])
@permission_required("marketing")
def update_affiliate(id):
    """Update an affiliate"""
    try:
        aff = Affiliate.query.get_or_404(id)
        data = request.get_json()
        if 'providerId' in data:
            aff.providerId = data['providerId']
        if 'category' in data:
            aff.category = data['category']
        if 'affiliateUrl' in data:
            aff.affiliateUrl = data['affiliateUrl']
        if 'linkName' in data:
            aff.linkName = data['linkName']
        if 'priority' in data:
            aff.priority = data['priority']
        if 'active' in data:
            aff.active = 1 if data['active'] else 0
        if 'country_code' in data:
            aff.country_code = data['country_code']
        aff.updatedAt = datetime.utcnow().isoformat()
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/affiliates/<id>', methods=['DELETE'])
@permission_required("marketing")
def delete_affiliate(id):
    """Delete an affiliate"""
    try:
        aff = Affiliate.query.get_or_404(id)
        db.session.delete(aff)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CAMPAIGNS
# ============================================================================

@marketing_bp.route('/campaigns', methods=['GET'])
@permission_required("marketing")
def get_campaigns():
    """List all campaigns"""
    try:
        country = getattr(request, 'user_country', 'US')
        camps = MarketingCampaign.query.filter(
            (MarketingCampaign.country_code == country) | 
            (MarketingCampaign.country_code == 'GLOBAL')
        ).order_by(MarketingCampaign.created_at.desc()).all()
        return jsonify({
            'campaigns': [{
                'id': c.id,
                'name': c.name,
                'description': c.description,
                'type': c.type,
                'status': c.status,
                'start_date': c.start_date.isoformat() if c.start_date else None,
                'end_date': c.end_date.isoformat() if c.end_date else None,
                'budget': float(c.budget) if c.budget else None,
                'created_at': c.created_at.isoformat() if c.created_at else None
            } for c in camps]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/campaigns', methods=['POST'])
@permission_required("marketing")
def create_campaign():
    """Create a campaign"""
    try:
        data = request.get_json()
        camp = MarketingCampaign(
            id=str(uuid.uuid4()),
            name=data['name'],
            description=data.get('description'),
            type=data.get('type'),
            status=data.get('status', 'draft'),
            budget=data.get('budget'),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(camp)
        db.session.commit()
        return jsonify({'ok': True, 'id': camp.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@marketing_bp.route('/campaigns/<id>', methods=['DELETE'])
@permission_required("marketing")
def delete_campaign(id):
    """Delete a campaign"""
    try:
        camp = MarketingCampaign.query.get_or_404(id)
        db.session.delete(camp)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
