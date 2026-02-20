from flask import Blueprint, request, jsonify
from routes.decorators import auth_required, admin_required
from models.subscription import SubscriptionPlan, SubscriptionCoupon, PaymentTransaction, UserSubscription
from models import db
from services.subscription.manager import SubscriptionManager
from services.subscription.gateways import get_payment_gateway
from services.subscription.constants import FeatureKeys, UsageLimits
from datetime import datetime

# ==========================================================
# SUBSCRIPTION ROUTES
# Purpose: Public and Authenticated endpoints for managing
# plans and payments.
# ==========================================================

subscription_bp = Blueprint('subscription', __name__)

@subscription_bp.route('/plans', methods=['GET'])
def list_plans():
    """
    Returns available subscription tiers for the pricing page.
    """
    plans = SubscriptionPlan.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in plans])


@subscription_bp.route('/verify-coupon', methods=['POST'])
@auth_required
def verify_coupon():
    """
    Checks if a coupon is valid and returns the discounted price.
    Used by frontend to show immediate feedback.
    """
    data = request.json
    plan_id = data.get('plan_id')
    coupon_code = data.get('coupon_code')
    
    if not plan_id:
        return jsonify({'error': 'plan_id is required'}), 400
        
    result, error = SubscriptionManager.calculate_final_price(plan_id, coupon_code)
    
    if error:
        return jsonify({'error': error}), 400
        
    return jsonify({
        'base_price': float(result['base_price']),
        'final_price': float(result['final_price']),
        'valid': True
    })


@subscription_bp.route('/checkout', methods=['POST'])
@auth_required
def checkout():
    """
    Initiates the payment process. 
    Returns the gateway's approval URL (e.g. PayPal checkout link).
    """
    data = request.json
    user = request.user
    plan_id = data.get('plan_id')
    coupon_code = data.get('coupon_code')
    is_trial = data.get('trial', False)
    gateway_type = data.get('gateway', 'stripe')  # Default to Stripe for trial support
    
    if not plan_id:
        return jsonify({'error': 'plan_id is required'}), 400
        
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': 'Invalid plan'}), 400

    # Trial validation
    if is_trial:
        if not plan.trial_enabled:
            return jsonify({'error': 'This plan does not support trial'}), 400
            
        # Fraud Prevention: Check if user already used trial
        if not SubscriptionManager.can_start_trial(user.id):
            return jsonify({'error': 'You have already used your free trial'}), 400
            
        # Note: Both Stripe and PayPal now support subscription trials

    # 1. Calculate final price (including discounts)
    calc_result, error = SubscriptionManager.calculate_final_price(plan_id, coupon_code)
    if error:
        return jsonify({'error': error}), 400
        
    final_price = calc_result['final_price']
    
    # 2. Get selected gateway (PayPal/Stripe)
    try:
        gateway = get_payment_gateway(gateway_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    # 3. Create order with provider
    # Pass trial_days if this is a trial checkout
    trial_days = plan.trial_days if is_trial and plan.trial_enabled else None
    
    provider_result, error = gateway.create_order(
        plan_name=plan.name,
        final_price=final_price,
        currency=plan.currency,
        trial_days=trial_days,
        plan_id=plan.id  # Pass plan_id so gateway can include it in success URL
    )
    
    if error:
        return jsonify({'error': 'Payment provider error', 'details': error}), 502
        
    return jsonify({
        'order_id': provider_result['order_id'],
        'approval_url': provider_result['approval_url'],
        'final_price': float(final_price),
        'is_trial': bool(trial_days),
        'plan_id': plan.id
    })


@subscription_bp.route('/capture', methods=['POST'])
@auth_required
def capture():
    """
    Confirmed by frontend after user pays on provider's site.
    This captures the actual money and unlocks the features.
    """
    data = request.json
    user = request.user
    order_id = data.get('order_id')
    plan_id = data.get('plan_id') # Needed to know what to activate
    gateway_type = data.get('gateway', 'stripe')  # Default to stripe
    
    if not order_id or not plan_id:
        return jsonify({'error': 'order_id and plan_id are required'}), 400
    
    # Convert plan_id to int (may come as string from JSON)
    try:
        plan_id = int(plan_id)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid plan_id format'}), 400
    
    # Validate plan exists
    plan = SubscriptionPlan.query.get(plan_id)
    if not plan:
        return jsonify({'error': f'Plan with id {plan_id} not found'}), 400
        
    # 1. IDEMPOTENCY CHECK: Prevent duplicate processing of the same order
    existing_tx = PaymentTransaction.query.filter_by(gateway_transaction_id=order_id).first()
    if existing_tx:
        return jsonify({
            'success': True, 
            'message': 'Order already processed.',
            'plan': existing_tx.subscription.plan.name if existing_tx.subscription else "Active"
        }), 200

    # 2. Finalize payment on gateway
    try:
        gateway = get_payment_gateway(gateway_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
        
    capture_result, error = gateway.capture_payment(order_id)
    
    if error:
        return jsonify({'error': 'Capture failed', 'details': error}), 400
        
    # 3. ATOMIC DATABASE TRANSACTION
    # We wrap both the subscription update and the transaction log in one try/except block
    try:
        gateway_name = getattr(gateway, '__class__', {}).__name__.replace('Gateway', '').lower()
        
        # Check if this is a trial (Stripe subscription with trial)
        is_trial = capture_result.get('is_trial', False)
        
        # This call now only adds to session, it does NOT commit
        sub = SubscriptionManager.activate_subscription(
            user_id=user.id,
            plan_id=plan_id,
            gateway=gateway_name,
            external_id=capture_result.get('transaction_id'),
            is_trial=is_trial
        )
        
        # Validate subscription was created
        if not sub or sub is False:
            return jsonify({'error': 'Failed to activate subscription'}), 500
        
        # Log the Transaction (Audit)
        transaction = PaymentTransaction(
            user_id=user.id,
            subscription_id=sub.id,
            amount=capture_result.get('amount', 0),
            currency='USD', 
            status='succeeded',
            gateway=gateway_name,
            gateway_transaction_id=order_id, # Link to the original Order ID for idempotency
            description=f"{'Trial' if is_trial else 'Initial Purchase'}: {sub.plan.name}"
        )
        db.session.add(transaction)
        
        # ONE SINGLE COMMIT for everything
        db.session.commit()
        
        # Send Subscription Receipt Email
        try:
            from notifications.email_service import send_subscription_success_email
            send_subscription_success_email(
                user.email, 
                user.name, 
                sub.plan.name, 
                capture_result.get('amount', 0)
            )
        except Exception as email_err:
            print(f"[Subscription] Failed to send receipt email: {email_err}")
        
        return jsonify({
            'success': True,
            'message': 'Subscription activated successfully!',
            'plan': sub.plan.name,
            'expiry': sub.current_period_end.isoformat(),
            'is_trial': sub.status == 'trialing'
        })

    except Exception as e:
        db.session.rollback() # Undo everything if even one part fails
        print(f"[Subscription ERROR] Atomic capture failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Internal system error during activation', 'message': str(e)}), 500


@subscription_bp.route('/cancel', methods=['POST'])
@auth_required
def cancel_subscription():
    """
    Cancels the user's active subscription.
    Marks status as 'cancelled' but keeps access until period end.
    """
    user = request.user
    
    # Get user's active subscription
    sub = UserSubscription.query.filter(
        UserSubscription.user_id == user.id,
        UserSubscription.status.in_(['active', 'trialing'])
    ).first()
    
    if not sub:
        return jsonify({'error': 'No active subscription found'}), 404
    
    # Cancel with payment gateway if we have an external subscription
    if sub.external_subscription_id:
        try:
            gateway = get_payment_gateway(sub.payment_gateway or 'stripe')
            success, message = gateway.cancel_subscription(sub.external_subscription_id)
            if not success:
                print(f"[Subscription] Gateway cancel warning: {message}")
        except Exception as e:
            print(f"[Subscription] Gateway cancel error: {e}")
    
    # Update database
    sub.status = 'cancelled'
    if hasattr(sub, 'auto_renew'):
        sub.auto_renew = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'Subscription cancelled successfully',
        'access_until': sub.current_period_end.isoformat() if sub.current_period_end else None
    })


# ==========================================================
# ADMIN SUB-ROUTES (Subscription Management)
# ==========================================================

@subscription_bp.route('/admin/available-features', methods=['GET'])
@admin_required
def admin_list_features():
    """
    Returns a list of all feature keys AND usage limit keys.
    This powers the checklist/dropdown in the Admin Dashboard.
    """
    return jsonify({
        'features': FeatureKeys.get_all(),
        'limits': UsageLimits.get_limit_keys(),
        'description': 'Use features for toggles and limits for numeric quotas.'
    })

@subscription_bp.route('/admin/plans', methods=['POST'])
@admin_required
def admin_create_plan():
    """Admin only: Create a new subscription tier"""
    data = request.json
    try:
        new_plan = SubscriptionPlan(
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            currency=data.get('currency', 'USD'),
            interval=data.get('interval', 'monthly'),
            duration_days=data.get('duration_days', 30),
            features=data.get('features', {}),
            max_members=data.get('max_members', 1),
            is_featured=data.get('is_featured', False),
            trial_enabled=data.get('trial_enabled', False),
            trial_days=data.get('trial_days', 7)
        )
        db.session.add(new_plan)
        db.session.commit()
        return jsonify({'message': 'Plan created', 'plan_id': new_plan.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/admin/plans/<int:plan_id>', methods=['PATCH'])
@admin_required
def admin_update_plan(plan_id):
    """Admin only: Update an existing plan and its features"""
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    data = request.json
    
    # Update fields if provided
    for key in ['name', 'description', 'price', 'features', 'is_active', 'is_featured', 'trial_enabled', 'trial_days']:
        if key in data:
            setattr(plan, key, data[key])
            
    db.session.commit()
    return jsonify({'message': 'Plan updated successfully'})

@subscription_bp.route('/admin/coupons', methods=['POST'])
@admin_required
def admin_create_coupon():
    """Admin only: Create marketing discount codes"""
    data = request.json
    from datetime import datetime
    try:
        new_coupon = SubscriptionCoupon(
            code=data['code'].upper().strip(),
            discount_type=data.get('discount_type', 'percent'),
            discount_value=data['discount_value'],
            valid_until=datetime.fromisoformat(data['valid_until']) if data.get('valid_until') else None,
            max_redemptions=data.get('max_redemptions'),
            is_active=True
        )
        db.session.add(new_coupon)
        db.session.commit()
        return jsonify({'message': 'Coupon created', 'coupon_id': new_coupon.id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@subscription_bp.route('/admin/plans/<int:plan_id>', methods=['DELETE'])
@admin_required
def admin_delete_plan(plan_id):
    """
    Admin only: Remove a subscription plan.
    SAFETY: Prevents deletion if users are currently tied to this plan.
    Recommended to use 'is_active=False' instead for historical records.
    """
    plan = SubscriptionPlan.query.get_or_404(plan_id)
    
    # Check if any users are currently on this plan
    usage_count = UserSubscription.query.filter_by(plan_id=plan_id).count()
    if usage_count > 0:
        return jsonify({
            'error': 'Cannot delete plan',
            'message': f'There are {usage_count} users currently subscribed to this plan. Please deactivate it (is_active=False) instead to prevent system errors.'
        }), 400
        
    db.session.delete(plan)
    db.session.commit()
    return jsonify({'message': 'Plan deleted successfully'})

@subscription_bp.route('/admin/coupons/<int:coupon_id>', methods=['DELETE'])
@admin_required
def admin_delete_coupon(coupon_id):
    """Admin only: Remove a discount coupon"""
    coupon = SubscriptionCoupon.query.get_or_404(coupon_id)
    db.session.delete(coupon)
    db.session.commit()
    return jsonify({'message': 'Coupon deleted successfully'})

@subscription_bp.route('/admin/transactions', methods=['GET'])
@admin_required
def admin_get_transactions():
    """Admin only: View global payment history for reporting"""
    txs = PaymentTransaction.query.order_by(PaymentTransaction.created_at.desc()).limit(100).all()
    result = []
    for tx in txs:
        result.append({
            'id': tx.id,
            'user': tx.user_id,
            'amount': float(tx.amount),
            'status': tx.status,
            'date': tx.created_at.isoformat(),
            'gateway': tx.gateway
        })
    return jsonify(result)
