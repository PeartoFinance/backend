"""
Admin Financial Routes
CRUD for Transactions, Deposits, Withdrawals
"""
import uuid
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from models import db, Transaction, Deposit, Withdrawal, User, AuditEvent
from ..decorators import admin_required, permission_required

financial_bp = Blueprint('admin_financial', __name__, url_prefix='/financial')


def log_audit(action, entity, entity_id, meta=None):
    """Log admin audit event"""
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


# ============================================================================
# TRANSACTIONS
# ============================================================================

@financial_bp.route('/transactions', methods=['GET'])
@permission_required("transactions_view")
def get_transactions():
    """List all transactions with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        tx_type = request.args.get('type')
        user_id = request.args.get('user_id', type=int)
        search = request.args.get('search', '')

        query = Transaction.query

        if status:
            query = query.filter_by(status=status)
        if tx_type:
            query = query.filter_by(type=tx_type)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if search:
            query = query.filter(
                (Transaction.reference.ilike(f'%{search}%')) |
                (Transaction.description.ilike(f'%{search}%'))
            )

        transactions = query.order_by(Transaction.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return jsonify({
            'transactions': [{
                'id': t.id,
                'userId': t.user_id,
                'type': t.type,
                'amount': float(t.amount) if t.amount else 0,
                'currency': t.currency,
                'status': t.status,
                'reference': t.reference,
                'description': t.description,
                'metaData': t.meta_data,
                'createdAt': t.created_at.isoformat() if t.created_at else None,
                'updatedAt': t.updated_at.isoformat() if t.updated_at else None,
            } for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/transactions/<transaction_id>', methods=['GET'])
@permission_required("transactions_view")
def get_transaction(transaction_id):
    """Get single transaction details"""
    try:
        tx = Transaction.query.get_or_404(transaction_id)
        user = User.query.get(tx.user_id)

        return jsonify({
            'id': tx.id,
            'userId': tx.user_id,
            'userName': user.name if user else 'Unknown',
            'userEmail': user.email if user else None,
            'type': tx.type,
            'amount': float(tx.amount) if tx.amount else 0,
            'currency': tx.currency,
            'status': tx.status,
            'reference': tx.reference,
            'description': tx.description,
            'metaData': tx.meta_data,
            'createdAt': tx.created_at.isoformat() if tx.created_at else None,
            'updatedAt': tx.updated_at.isoformat() if tx.updated_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/transactions/<transaction_id>/status', methods=['PUT'])
@permission_required("transactions_view")
def update_transaction_status(transaction_id):
    """Update transaction status"""
    try:
        tx = Transaction.query.get_or_404(transaction_id)
        data = request.get_json()

        old_status = tx.status
        new_status = data.get('status')

        if new_status not in ['pending', 'completed', 'failed', 'cancelled']:
            return jsonify({'error': 'Invalid status'}), 400

        # CRITICAL: Prepare the audit log BEFORE committing the transaction.
        # This ensures the status change and the log entry are saved together.
        log_audit('TRANSACTION_STATUS_UPDATE', 'transaction', transaction_id, {
            'old': old_status, 'new': new_status
        })

        db.session.commit()

        return jsonify({'ok': True, 'message': f'Status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# DEPOSITS
# ============================================================================

@financial_bp.route('/deposits', methods=['GET'])
@permission_required("deposits_manage")
def get_deposits():
    """List all deposits with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)

        query = Deposit.query

        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)

        deposits = query.order_by(Deposit.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get user info for each deposit
        user_ids = list(set(d.user_id for d in deposits.items))
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

        return jsonify({
            'deposits': [{
                'id': d.id,
                'userId': d.user_id,
                'userName': users.get(d.user_id, {}).name if users.get(d.user_id) else 'Unknown',
                'userEmail': users.get(d.user_id, {}).email if users.get(d.user_id) else None,
                'amount': float(d.amount) if d.amount else 0,
                'currency': d.currency,
                'paymentMethod': d.payment_method,
                'status': d.status,
                'transactionRef': d.transaction_ref,
                'createdAt': d.created_at.isoformat() if d.created_at else None,
            } for d in deposits.items],
            'total': deposits.total,
            'pages': deposits.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/deposits/<deposit_id>', methods=['GET'])
@permission_required("deposits_manage")
def get_deposit(deposit_id):
    """Get single deposit details"""
    try:
        d = Deposit.query.get_or_404(deposit_id)
        user = User.query.get(d.user_id)

        return jsonify({
            'id': d.id,
            'userId': d.user_id,
            'userName': user.name if user else 'Unknown',
            'userEmail': user.email if user else None,
            'amount': float(d.amount) if d.amount else 0,
            'currency': d.currency,
            'paymentMethod': d.payment_method,
            'status': d.status,
            'transactionRef': d.transaction_ref,
            'createdAt': d.created_at.isoformat() if d.created_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/deposits/<deposit_id>/status', methods=['PUT'])
@permission_required("deposits_manage")
def update_deposit_status(deposit_id):
    """Update deposit status"""
    try:
        d = Deposit.query.get_or_404(deposit_id)
        data = request.get_json()

        old_status = d.status
        new_status = data.get('status')

        if new_status not in ['pending', 'completed', 'failed']:
            return jsonify({'error': 'Invalid status'}), 400

        d.status = new_status
        
        # Prepare log before commit to ensure it's saved to the DB
        log_audit('DEPOSIT_STATUS_UPDATE', 'deposit', deposit_id, {
            'old': old_status, 'new': new_status, 'amount': float(d.amount)
        })

        db.session.commit()

        return jsonify({'ok': True, 'message': f'Deposit status updated to {new_status}'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# WITHDRAWALS
# ============================================================================

@financial_bp.route('/withdrawals', methods=['GET'])
@permission_required("withdrawals_manage")
def get_withdrawals():
    """List all withdrawals with filters"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        user_id = request.args.get('user_id', type=int)

        query = Withdrawal.query

        if status:
            query = query.filter_by(status=status)
        if user_id:
            query = query.filter_by(user_id=user_id)

        withdrawals = query.order_by(Withdrawal.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        # Get user info
        user_ids = list(set(w.user_id for w in withdrawals.items))
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()}

        return jsonify({
            'withdrawals': [{
                'id': w.id,
                'userId': w.user_id,
                'userName': users.get(w.user_id).name if users.get(w.user_id) else 'Unknown',
                'userEmail': users.get(w.user_id).email if users.get(w.user_id) else None,
                'amount': float(w.amount) if w.amount else 0,
                'currency': w.currency,
                'paymentMethod': w.payment_method,
                'accountDetails': w.account_details,
                'status': w.status,
                'approvedBy': w.approved_by,
                'createdAt': w.created_at.isoformat() if w.created_at else None,
                'processedAt': w.processed_at.isoformat() if w.processed_at else None,
            } for w in withdrawals.items],
            'total': withdrawals.total,
            'pages': withdrawals.pages,
            'currentPage': page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/withdrawals/<withdrawal_id>', methods=['GET'])
@permission_required("withdrawals_manage")
def get_withdrawal(withdrawal_id):
    """Get single withdrawal details"""
    try:
        w = Withdrawal.query.get_or_404(withdrawal_id)
        user = User.query.get(w.user_id)
        approver = User.query.get(w.approved_by) if w.approved_by else None

        return jsonify({
            'id': w.id,
            'userId': w.user_id,
            'userName': user.name if user else 'Unknown',
            'userEmail': user.email if user else None,
            'amount': float(w.amount) if w.amount else 0,
            'currency': w.currency,
            'paymentMethod': w.payment_method,
            'accountDetails': w.account_details,
            'status': w.status,
            'approvedBy': w.approved_by,
            'approverName': approver.name if approver else None,
            'createdAt': w.created_at.isoformat() if w.created_at else None,
            'processedAt': w.processed_at.isoformat() if w.processed_at else None,
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/withdrawals/<withdrawal_id>/approve', methods=['PUT'])
@permission_required("withdrawals_manage")
def approve_withdrawal(withdrawal_id):
    """Approve a pending withdrawal"""
    try:
        w = Withdrawal.query.get_or_404(withdrawal_id)
        data = request.get_json()

        if w.status != 'pending':
            return jsonify({'error': f'Cannot approve withdrawal with status: {w.status}'}), 400

        admin_id = data.get('adminId')  # Should come from session in production

        w.status = 'approved'
        w.approved_by = admin_id
        
        # Log the approval action within the same transaction
        log_audit('WITHDRAWAL_APPROVED', 'withdrawal', withdrawal_id, {
            'amount': float(w.amount), 'userId': w.user_id
        })

        db.session.commit()

        return jsonify({'ok': True, 'message': 'Withdrawal approved'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/withdrawals/<withdrawal_id>/reject', methods=['PUT'])
@permission_required("withdrawals_manage")
def reject_withdrawal(withdrawal_id):
    """Reject a pending withdrawal"""
    try:
        w = Withdrawal.query.get_or_404(withdrawal_id)
        data = request.get_json()

        if w.status != 'pending':
            return jsonify({'error': f'Cannot reject withdrawal with status: {w.status}'}), 400

        w.status = 'rejected'
        
        # Log rejection within the same transaction record
        log_audit('WITHDRAWAL_REJECTED', 'withdrawal', withdrawal_id, {
            'amount': float(w.amount), 'userId': w.user_id, 'reason': data.get('reason')
        })

        db.session.commit()

        return jsonify({'ok': True, 'message': 'Withdrawal rejected'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@financial_bp.route('/withdrawals/<withdrawal_id>/process', methods=['PUT'])
@permission_required("withdrawals_manage")
def process_withdrawal(withdrawal_id):
    """Mark an approved withdrawal as processed/completed"""
    try:
        w = Withdrawal.query.get_or_404(withdrawal_id)

        if w.status != 'approved':
            return jsonify({'error': 'Can only process approved withdrawals'}), 400

        w.status = 'completed'
        w.processed_at = datetime.utcnow()
        
        # Log processing completion
        log_audit('WITHDRAWAL_PROCESSED', 'withdrawal', withdrawal_id, {
            'amount': float(w.amount), 'userId': w.user_id
        })

        db.session.commit()

        return jsonify({'ok': True, 'message': 'Withdrawal processed and completed'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ============================================================================
# STATS
# ============================================================================

@financial_bp.route('/stats', methods=['GET'])
@permission_required("financial")
def get_financial_stats():
    """Get financial overview stats"""
    try:
        from sqlalchemy import func

        # Transaction stats
        total_transactions = Transaction.query.count()
        pending_transactions = Transaction.query.filter_by(status='pending').count()

        # Deposit stats
        total_deposits = Deposit.query.count()
        pending_deposits = Deposit.query.filter_by(status='pending').count()
        total_deposit_amount = db.session.query(
            func.sum(Deposit.amount)
        ).filter_by(status='completed').scalar() or 0

        # Withdrawal stats
        total_withdrawals = Withdrawal.query.count()
        pending_withdrawals = Withdrawal.query.filter_by(status='pending').count()
        total_withdrawal_amount = db.session.query(
            func.sum(Withdrawal.amount)
        ).filter_by(status='completed').scalar() or 0

        return jsonify({
            'transactions': {
                'total': total_transactions,
                'pending': pending_transactions,
            },
            'deposits': {
                'total': total_deposits,
                'pending': pending_deposits,
                'totalAmount': float(total_deposit_amount),
            },
            'withdrawals': {
                'total': total_withdrawals,
                'pending': pending_withdrawals,
                'totalAmount': float(total_withdrawal_amount),
            },
            'netFlow': float(total_deposit_amount) - float(total_withdrawal_amount),
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
