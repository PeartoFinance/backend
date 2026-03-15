"""
Admin Orders Routes
Read-only order management
"""
import json
import uuid
from flask import Blueprint, jsonify, request
from models import db, Order, OrderItem, User, AuditEvent
from ..decorators import admin_required, permission_required

orders_bp = Blueprint('admin_orders', __name__, url_prefix='/orders')


def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin',
            action=action,
            entity=entity,
            entityId=entity_id,
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")


@orders_bp.route('', methods=['GET'])
@permission_required("orders_manage")
def get_orders():
    """List all orders with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)

        query = Order.query

        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)

        orders = query.order_by(Order.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get users
        user_ids = list(set(o.user_id for o in orders.items))
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

        return jsonify({
            'orders': [{
                'id': o.id,
                'orderNumber': o.order_number,
                'userId': o.user_id,
                'userName': users.get(o.user_id).name if users.get(o.user_id) else 'Unknown',
                'status': o.status,
                'totalAmount': float(o.total_amount) if o.total_amount else 0,
                'currency': o.currency,
                'createdAt': o.created_at.isoformat() if o.created_at else None,
            } for o in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>', methods=['GET'])
@permission_required("orders_manage")
def get_order(order_id):
    """Get single order with items"""
    try:
        order = Order.query.get_or_404(order_id)
        user = User.query.get(order.user_id)
        items = OrderItem.query.filter_by(order_id=order_id).all()

        return jsonify({
            'id': order.id,
            'orderNumber': order.order_number,
            'userId': order.user_id,
            'userName': user.name if user else 'Unknown',
            'userEmail': user.email if user else None,
            'status': order.status,
            'totalAmount': float(order.total_amount) if order.total_amount else 0,
            'currency': order.currency,
            'shippingAddress': order.shipping_address,
            'billingAddress': order.billing_address,
            'notes': order.notes,
            'items': [{
                'id': item.id,
                'productId': item.product_id,
                'productName': item.product_name,
                'quantity': item.quantity,
                'unitPrice': float(item.unit_price) if item.unit_price else 0,
                'totalPrice': float(item.total_price) if item.total_price else 0,
            } for item in items],
            'createdAt': order.created_at.isoformat() if order.created_at else None,
            'updatedAt': order.updated_at.isoformat() if order.updated_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/<order_id>/status', methods=['PUT'])
@permission_required("orders_manage")
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()

        old_status = order.status
        new_status = data.get('status')

        valid_statuses = ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        order.status = new_status
        db.session.commit()

        log_audit('ORDER_STATUS_UPDATE', 'order', order_id, {
            'old': old_status, 'new': new_status
        })

        return jsonify({'ok': True, 'message': f'Order status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@orders_bp.route('/stats', methods=['GET'])
@permission_required("orders_manage")
def get_order_stats():
    """Get order statistics"""
    try:
        from sqlalchemy import func

        total_orders = Order.query.count()
        pending = Order.query.filter_by(status='pending').count()
        confirmed = Order.query.filter_by(status='confirmed').count()
        shipped = Order.query.filter_by(status='shipped').count()
        delivered = Order.query.filter_by(status='delivered').count()
        cancelled = Order.query.filter_by(status='cancelled').count()

        total_revenue = db.session.query(
            func.sum(Order.total_amount)
        ).filter(Order.status.in_(['confirmed', 'shipped', 'delivered'])).scalar() or 0

        return jsonify({
            'total': total_orders,
            'pending': pending,
            'confirmed': confirmed,
            'shipped': shipped,
            'delivered': delivered,
            'cancelled': cancelled,
            'totalRevenue': float(total_revenue),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
