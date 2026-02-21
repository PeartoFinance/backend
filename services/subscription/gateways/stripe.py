import stripe
import os
from .base import PaymentGateway
from services.settings_service import get_setting_secure

# ==========================================================
# STRIPE ADAPTER
# Purpose: Implements the 'PaymentGateway' interface for Stripe.
# 
# DESIGN CHOICE:
# Uses Stripe Checkout Sessions for a secure, hosted payment page.
# For trials, uses subscription mode with trial_period_days.
# This ensures card is collected upfront for billing after trial.
# ==========================================================

class StripeGateway(PaymentGateway):
    def __init__(self):
        # Get return/cancel URLs
        self.success_url = get_setting_secure('STRIPE_SUCCESS_URL', 'http://localhost:3000/subscription/success')
        self.cancel_url = get_setting_secure('STRIPE_CANCEL_URL', 'http://localhost:3000/pricing')

    def _set_api_key(self):
        """Fetch and set Stripe API key dynamically"""
        stripe.api_key = get_setting_secure('STRIPE_SECRET_KEY')

    def create_order(self, plan_name, final_price, currency="USD", trial_days=None, plan_id=None):
        """
        Creates a Stripe Checkout Session.
        If trial_days is provided, creates a subscription with trial period.
        Otherwise creates a one-time payment.
        """
        try:
            # Convert price to cents (Stripe uses smallest currency unit)
            self._set_api_key()
            amount_cents = int(float(final_price) * 100)
            
            if trial_days and trial_days > 0:
                # For trials, create a subscription with trial period
                # First create a dynamic price
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': currency.lower(),
                            'product_data': {
                                'name': f'Pearto Finance: {plan_name}',
                                'description': f'Subscription to {plan_name} plan',
                            },
                            'unit_amount': amount_cents,
                            'recurring': {
                                'interval': 'month',
                            },
                        },
                        'quantity': 1,
                    }],
                    mode='subscription',
                    subscription_data={
                        'trial_period_days': trial_days,
                    },
                    success_url=f"{self.success_url}?session_id={{CHECKOUT_SESSION_ID}}&gateway=stripe&plan_id={plan_id}",
                    cancel_url=self.cancel_url,
                )
            else:
                # One-time payment
                session = stripe.checkout.Session.create(
                    payment_method_types=['card'],
                    line_items=[{
                        'price_data': {
                            'currency': currency.lower(),
                            'product_data': {
                                'name': f'Pearto Finance: {plan_name}',
                                'description': f'Subscription to {plan_name} plan',
                            },
                            'unit_amount': amount_cents,
                        },
                        'quantity': 1,
                    }],
                    mode='payment',
                    success_url=f"{self.success_url}?session_id={{CHECKOUT_SESSION_ID}}&gateway=stripe&plan_id={plan_id}",
                    cancel_url=self.cancel_url,
                )
            
            return {
                'order_id': session.id,
                'approval_url': session.url
            }, None
            
        except stripe.error.StripeError as e:
            return None, str(e)

    def capture_payment(self, session_id):
        """
        Verifies Stripe Checkout Session completion.
        Handles both one-time payments and subscriptions (including trials).
        """
        try:
            self._set_api_key()
            session = stripe.checkout.Session.retrieve(session_id)
            
            # Handle subscription mode (including trials)
            if session.mode == 'subscription':
                subscription_id = session.subscription
                if subscription_id:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    is_trial = subscription.status == 'trialing'
                    return {
                        'success': True,
                        'transaction_id': subscription_id,
                        'amount': 0 if is_trial else str(session.amount_total / 100),
                        'is_trial': is_trial
                    }, None
                else:
                    return False, "No subscription created"
            
            # Handle payment mode (one-time)
            if session.payment_status == 'paid':
                return {
                    'success': True,
                    'transaction_id': session.payment_intent,
                    'amount': str(session.amount_total / 100),  # Convert back from cents
                    'is_trial': False
                }, None
            else:
                return False, f"Payment status: {session.payment_status}"
                
        except stripe.error.StripeError as e:
            return False, str(e)

    def cancel_subscription(self, external_sub_id):
        """
        Cancels a Stripe subscription.
        For one-time payments, this is a no-op.
        """
        if not external_sub_id or external_sub_id.startswith('cs_'):
            # Checkout session ID, not a subscription
            return True, "One-time payment, no subscription to cancel"
            
        try:
            self._set_api_key()
            stripe.Subscription.cancel(external_sub_id)
            return True, "Subscription cancelled"
        except stripe.error.StripeError as e:
            return False, str(e)

    def handle_webhook(self, data):
        """
        Processes Stripe webhook events.
        Common events: checkout.session.completed, invoice.paid, customer.subscription.deleted
        """
        event_type = data.get('type')
        
        # Handle different event types
        if event_type == 'checkout.session.completed':
            session = data['data']['object']
            return {
                'processed': True,
                'event': event_type,
                'session_id': session['id']
            }
        
        return {'processed': True, 'event': event_type}
