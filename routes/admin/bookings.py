"""
Admin Bookings Routes
CRUD for Service Bookings
"""
import json
import uuid
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Booking, User, AuditEvent
from ..decorators import admin_required, permission_required

bookings_bp = Blueprint('admin_bookings', __name__, url_prefix='/bookings')


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


@bookings_bp.route('', methods=['GET'])
@permission_required("bookings")
def get_bookings():
    """List all bookings with pagination and filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        search = request.args.get('search', '')

        query = Booking.query

        if status:
            query = query.filter_by(status=status)
        if search:
            query = query.filter(
                (Booking.name.ilike(f'%{search}%')) |
                (Booking.email.ilike(f'%{search}%')) |
                (Booking.service.ilike(f'%{search}%'))
            )

        bookings = query.order_by(Booking.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'bookings': [{
                'id': b.id,
                'userName': b.name or f"{b.firstName or ''} {b.lastName or ''}".strip() or b.email,
                'email': b.email,
                'phone': b.phone,
                'serviceName': b.service,
                'date': b.date.isoformat() if b.date else None,
                'time': b.time,
                'status': b.status,
                'notes': b.notes,
                'createdAt': b.created_at.isoformat() if b.created_at else None,
            } for b in bookings.items],
            'total': bookings.total,
            'pages': bookings.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bookings_bp.route('/<booking_id>', methods=['GET'])
@permission_required("bookings")
def get_booking(booking_id):
    """Get single booking details"""
    try:
        b = Booking.query.get_or_404(booking_id)

        return jsonify({
            'id': b.id,
            'name': b.name,
            'firstName': b.firstName,
            'lastName': b.lastName,
            'email': b.email,
            'phone': b.phone,
            'service': b.service,
            'date': b.date.isoformat() if b.date else None,
            'time': b.time,
            'status': b.status,
            'notes': b.notes,
            'countryCode': b.country_code,
            'createdAt': b.created_at.isoformat() if b.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bookings_bp.route('/<booking_id>/status', methods=['PUT'])
@permission_required("bookings")
def update_booking_status(booking_id):
    """Update booking status"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()

        new_status = data.get('status')
        valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']

        if new_status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400

        old_status = booking.status
        booking.status = new_status

        db.session.commit()
        log_audit('BOOKING_STATUS_UPDATE', 'booking', booking_id, {
            'oldStatus': old_status,
            'newStatus': new_status
        })

        return jsonify({'ok': True, 'message': f'Booking {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bookings_bp.route('/<booking_id>', methods=['PUT'])
@permission_required("bookings")
def update_booking(booking_id):
    """Update booking details"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()

        if 'name' in data:
            booking.name = data['name']
        if 'email' in data:
            booking.email = data['email']
        if 'phone' in data:
            booking.phone = data['phone']
        if 'service' in data:
            booking.service = data['service']
        if 'date' in data:
            booking.date = datetime.strptime(data['date'], '%Y-%m-%d').date() if data['date'] else None
        if 'time' in data:
            booking.time = data['time']
        if 'notes' in data:
            booking.notes = data['notes']
        if 'status' in data:
            booking.status = data['status']

        db.session.commit()
        log_audit('BOOKING_UPDATE', 'booking', booking_id, data)

        return jsonify({'ok': True, 'message': 'Booking updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bookings_bp.route('/<booking_id>', methods=['DELETE'])
@permission_required("bookings")
def delete_booking(booking_id):
    """Delete a booking"""
    try:
        booking = Booking.query.get_or_404(booking_id)

        db.session.delete(booking)
        db.session.commit()

        log_audit('BOOKING_DELETE', 'booking', booking_id)

        return jsonify({'ok': True, 'message': 'Booking deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bookings_bp.route('/stats', methods=['GET'])
@permission_required("bookings")
def get_booking_stats():
    """Get booking statistics"""
    try:
        total = Booking.query.count()
        pending = Booking.query.filter_by(status='pending').count()
        confirmed = Booking.query.filter_by(status='confirmed').count()
        completed = Booking.query.filter_by(status='completed').count()
        cancelled = Booking.query.filter_by(status='cancelled').count()

        return jsonify({
            'total': total,
            'pending': pending,
            'confirmed': confirmed,
            'completed': completed,
            'cancelled': cancelled,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
