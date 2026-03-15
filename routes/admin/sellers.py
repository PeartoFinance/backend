"""
Admin Sellers Routes
Manage sellers and seller applications
"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Seller, SellerApplication, User, AuditEvent
from ..decorators import admin_required, permission_required

sellers_bp = Blueprint('admin_sellers', __name__, url_prefix='/sellers')


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


# ============================================================================
# SELLERS
# ============================================================================

@sellers_bp.route('', methods=['GET'])
@permission_required("sellers_manage")
def get_sellers():
    """List all sellers"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search', '')

        query = Seller.query

        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(Seller.business_name.ilike(f'%{search}%'))

        sellers = query.order_by(Seller.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get users
        user_ids = list(set(s.user_id for s in sellers.items))
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

        return jsonify({
            'sellers': [{
                'id': s.id,
                'userId': s.user_id,
                'userName': users.get(s.user_id).name if users.get(s.user_id) else 'Unknown',
                'businessName': s.business_name,
                'description': s.description,
                'logoUrl': s.logo_url,
                'status': s.status,
                'rating': float(s.rating) if s.rating else 0,
                'totalSales': s.total_sales,
                'createdAt': s.created_at.isoformat() if s.created_at else None,
            } for s in sellers.items],
            'total': sellers.total,
            'pages': sellers.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sellers_bp.route('/<seller_id>', methods=['GET'])
@permission_required("sellers_manage")
def get_seller(seller_id):
    """Get seller details"""
    try:
        s = Seller.query.get_or_404(seller_id)
        user = User.query.get(s.user_id) if s.user_id else None

        return jsonify({
            'id': s.id,
            'userId': s.user_id,
            'userName': user.name if user else None,
            'userEmail': user.email if user else None,
            'businessName': s.business_name,
            'description': s.description,
            'logoUrl': s.logo_url,
            'status': s.status,
            'rating': float(s.rating) if s.rating else 0,
            'totalSales': s.total_sales,
            'countryCode': s.country_code,
            'createdAt': s.created_at.isoformat() if s.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sellers_bp.route('/<seller_id>/status', methods=['PUT'])
@permission_required("sellers_manage")
def update_seller_status(seller_id):
    """Update seller status"""
    try:
        seller = Seller.query.get_or_404(seller_id)
        data = request.get_json()

        old_status = seller.status
        new_status = data.get('status')

        valid_statuses = ['pending', 'approved', 'suspended']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        seller.status = new_status
        db.session.commit()

        log_audit('SELLER_STATUS_UPDATE', 'seller', seller_id, {
            'old': old_status, 'new': new_status
        })

        return jsonify({'ok': True, 'message': f'Seller status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# SELLER APPLICATIONS
# ============================================================================

@sellers_bp.route('/applications', methods=['GET'])
@permission_required("sellers_manage")
def get_applications():
    """List all seller applications"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')

        query = SellerApplication.query

        if status:
            query = query.filter_by(status=status)

        apps = query.order_by(SellerApplication.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get users
        user_ids = list(set(a.user_id for a in apps.items if a.user_id))
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

        return jsonify({
            'applications': [{
                'id': a.id,
                'userId': a.user_id,
                'userName': users.get(a.user_id).name if users.get(a.user_id) else 'Unknown',
                'businessName': a.business_name,
                'businessType': a.business_type,
                'status': a.status,
                'createdAt': a.created_at.isoformat() if a.created_at else None,
            } for a in apps.items],
            'total': apps.total,
            'pages': apps.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sellers_bp.route('/applications/<int:app_id>', methods=['GET'])
@permission_required("sellers_manage")
def get_application(app_id):
    """Get application details"""
    try:
        a = SellerApplication.query.get_or_404(app_id)
        user = User.query.get(a.user_id) if a.user_id else None

        return jsonify({
            'id': a.id,
            'userId': a.user_id,
            'userName': user.name if user else None,
            'userEmail': user.email if user else None,
            'businessName': a.business_name,
            'businessType': a.business_type,
            'description': a.description,
            'documents': a.documents,
            'status': a.status,
            'notes': a.notes,
            'createdAt': a.created_at.isoformat() if a.created_at else None,
            'reviewedAt': a.reviewed_at.isoformat() if a.reviewed_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@sellers_bp.route('/applications/<int:app_id>/approve', methods=['PUT'])
@permission_required("sellers_manage")
def approve_application(app_id):
    """Approve a seller application"""
    try:
        app = SellerApplication.query.get_or_404(app_id)

        if app.status != 'pending':
            return jsonify({'error': 'Can only approve pending applications'}), 400

        # Create seller from application
        seller_id = str(uuid.uuid4())
        seller = Seller(
            id=seller_id,
            user_id=app.user_id,
            business_name=app.business_name,
            description=app.description,
            status='approved',
            created_at=datetime.utcnow()
        )

        db.session.add(seller)

        app.status = 'approved'
        app.reviewed_at = datetime.utcnow()

        db.session.commit()

        log_audit('SELLER_APPLICATION_APPROVED', 'seller_application', app_id, {
            'businessName': app.business_name
        })

        return jsonify({'ok': True, 'message': 'Application approved', 'sellerId': seller.id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@sellers_bp.route('/applications/<int:app_id>/reject', methods=['PUT'])
@permission_required("sellers_manage")
def reject_application(app_id):
    """Reject a seller application"""
    try:
        app = SellerApplication.query.get_or_404(app_id)
        data = request.get_json()

        if app.status != 'pending':
            return jsonify({'error': 'Can only reject pending applications'}), 400

        app.status = 'rejected'
        app.notes = data.get('reason', '')
        app.reviewed_at = datetime.utcnow()

        db.session.commit()

        log_audit('SELLER_APPLICATION_REJECTED', 'seller_application', app_id, {
            'reason': data.get('reason')
        })

        return jsonify({'ok': True, 'message': 'Application rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
