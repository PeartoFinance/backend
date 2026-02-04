from datetime import datetime, timedelta
from decimal import Decimal
from models.subscription import SubscriptionPlan, SubscriptionCoupon, UserSubscription, PaymentTransaction
from models import db

# ==========================================================
# SUBSCRIPTION MANAGER
# Purpose: This is the 'Brain' of the subscription domain.
# All business rules (access checks, pricing, plan switches)
# live here. This ensures that the Routes (controllers)
# stay clean and don't need to know about DB internals.
# ==========================================================

class SubscriptionManager:
    
    @staticmethod
    def get_user_subscription(user_id):
        """
        Retrieves the active subscription for a user.
        Includes a check for the expiry date (current_period_end).
        """
        sub = UserSubscription.query.filter_by(user_id=user_id, status='active').first()
        
        # If subscription exists but period has ended, it's virtually expired
        if sub and sub.current_period_end < datetime.utcnow():
            # Note: In a real system, a 'Grace Period' could be added here
            return None
            
        return sub

    @staticmethod
    def check_access(user_id, feature_key):
        """
        Determines if a user has access to a specific feature.
        
        Logic:
        1. Find active subscription.
        2. Get the specific Plan.
        3. Check if 'feature_key' is True/Numeric in the Plan's JSON features.
        """
        sub = SubscriptionManager.get_user_subscription(user_id)
        if not sub:
            return False
            
        plan = sub.plan
        if not plan or not plan.features:
            return False
            
        # Check if the feature exists in the JSON dict and is truthy
        feature_val = plan.features.get(feature_key)
        
        # If feature is boolean, check if True. If numeric (like max_ports), check > 0
        if isinstance(feature_val, bool):
            return feature_val
        elif isinstance(feature_val, (int, float)):
            return feature_val > 0
            
        return False

    @staticmethod
    def calculate_final_price(plan_id, coupon_code=None):
        """
        Calculates the amount to charge a user.
        
        Handles:
        1. Base Plan Price.
        2. Coupon code application (Percentage or Fixed).
        3. Validation of coupon expiry and limits.
        """
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return None, "Invalid Plan"
            
        base_price = Decimal(str(plan.price))
        final_price = base_price
        applied_coupon = None
        
        if coupon_code:
            coupon = SubscriptionCoupon.query.filter_by(
                code=coupon_code.upper().strip(), 
                is_active=True
            ).first()
            
            # Validation Logic
            if not coupon:
                return None, "Invalid Coupon Code"
            
            if coupon.valid_until and coupon.valid_until < datetime.utcnow():
                return None, "Coupon has expired"
                
            if coupon.max_redemptions and coupon.times_redeemed >= coupon.max_redemptions:
                return None, "Coupon usage limit reached"
            
            # Application Logic
            if coupon.discount_type == 'percent':
                discount = (base_price * Decimal(str(coupon.discount_value))) / Decimal('100')
                final_price = base_price - discount
            else:
                final_price = base_price - Decimal(str(coupon.discount_value))
            
            # Ensure price never goes below zero and ROUND to 2 decimal places for payment gateways
            final_price = max(final_price, Decimal('0.00'))
            final_price = final_price.quantize(Decimal('0.01'))
            applied_coupon = coupon

        return {
            'base_price': base_price,
            'final_price': final_price,
            'coupon': applied_coupon
        }, None

    @staticmethod
    def activate_subscription(user_id, plan_id, gateway, external_id=None):
        """
        Called after a successful payment!
        Creates or updates the UserSubscription record.
        """
        plan = SubscriptionPlan.query.get(plan_id)
        if not plan:
            return False
            
        # Check for existing sub to update, or create new
        sub = UserSubscription.query.filter_by(user_id=user_id).first()
        
        expiry_date = datetime.utcnow() + timedelta(days=plan.duration_days)
        
        if sub:
            sub.plan_id = plan.id
            sub.status = 'active'
            sub.current_period_end = expiry_date
            sub.payment_gateway = gateway
            sub.external_subscription_id = external_id
        else:
            sub = UserSubscription(
                user_id=user_id,
                plan_id=plan.id,
                status='active',
                current_period_end=expiry_date,
                payment_gateway=gateway,
                external_subscription_id=external_id
            )
            db.session.add(sub)
            
        db.session.commit()
        return sub
