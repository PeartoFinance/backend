import requests
import json
import os
from datetime import datetime, timedelta
from .base import PaymentGateway
from services.settings_service import get_setting_secure

# ==========================================================
# PAYPAL ADAPTER
# Purpose: Implements the 'PaymentGateway' interface for PayPal.
# 
# DESIGN CHOICE:
# We use direct 'requests' calls instead of a heavy SDK.
# This makes the code very lightweight and easy to debug.
# All environment variables (CLIENT_ID, SECRET) are loaded
# from '.env' so the developer can use their own sandbox keys.
#
# SUBSCRIPTION SUPPORT:
# For trials and recurring billing, we use PayPal Subscriptions API
# which requires a Product and Plan to be created first.
# ==========================================================

class PayPalGateway(PaymentGateway):
    def __init__(self):
        # Determine if we are in Sandbox (testing) or Live mode
        self.mode = get_setting_secure('PAYPAL_MODE', 'sandbox')
        if self.mode == 'live':
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"
        
        self.return_url = get_setting_secure('PAYPAL_RETURN_URL')
        self.cancel_url = get_setting_secure('PAYPAL_CANCEL_URL')

    def _get_access_token(self):
        """
        Internal helper to authenticate with PayPal.
        Returns the OAuth2 Bearer token.
        """
        url = f"{self.base_url}/v1/oauth2/token"
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en_US",
        }
        data = {"grant_type": "client_credentials"}
        
        # PayPal uses 'Basic Auth' with (Client_ID:Secret) encoded in Base64
        client_id = get_setting_secure('PAYPAL_CLIENT_ID')
        secret = get_setting_secure('PAYPAL_SECRET')
        
        response = requests.post(
            url, 
            auth=(client_id, secret), 
            headers=headers, 
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"[PayPal] Failed to get Access Token: {response.text}")
            return None

    def _create_product(self, token, plan_name):
        """Create a PayPal product (required for subscriptions)."""
        url = f"{self.base_url}/v1/catalogs/products"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "name": f"Pearto Finance: {plan_name}",
            "description": f"Subscription to {plan_name}",
            "type": "SERVICE",
            "category": "SOFTWARE"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json().get('id'), None
        return None, response.text

    def _create_billing_plan(self, token, product_id, plan_name, price, currency, trial_days=None):
        """Create a PayPal billing plan with optional trial period."""
        url = f"{self.base_url}/v1/billing/plans"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        billing_cycles = []
        sequence = 1
        
        # Add trial cycle if trial_days > 0
        if trial_days and trial_days > 0:
            billing_cycles.append({
                "frequency": {
                    "interval_unit": "DAY",
                    "interval_count": trial_days
                },
                "tenure_type": "TRIAL",
                "sequence": sequence,
                "total_cycles": 1,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "0",
                        "currency_code": currency
                    }
                }
            })
            sequence += 1
        
        # Add regular billing cycle
        billing_cycles.append({
            "frequency": {
                "interval_unit": "MONTH",
                "interval_count": 1
            },
            "tenure_type": "REGULAR",
            "sequence": sequence,
            "total_cycles": 0,  # 0 means infinite
            "pricing_scheme": {
                "fixed_price": {
                    "value": str(price),
                    "currency_code": currency
                }
            }
        })
        
        payload = {
            "product_id": product_id,
            "name": f"{plan_name} Monthly",
            "description": f"Monthly subscription to {plan_name}",
            "billing_cycles": billing_cycles,
            "payment_preferences": {
                "auto_bill_outstanding": True,
                "payment_failure_threshold": 3
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            return response.json().get('id'), None
        return None, response.text

    def _create_subscription(self, token, billing_plan_id, plan_id=None):
        """Create a PayPal subscription."""
        url = f"{self.base_url}/v1/billing/subscriptions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        payload = {
            "plan_id": billing_plan_id,
            "application_context": {
                "brand_name": "Pearto Finance",
                "return_url": f"{self.return_url}?gateway=paypal&plan_id={plan_id}",
                "cancel_url": self.cancel_url,
                "user_action": "SUBSCRIBE_NOW"
            }
        }
        
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            subscription_id = data.get('id')
            # Extract the 'approve' link for the user
            approve_url = next((link['href'] for link in data.get('links', []) if link['rel'] == 'approve'), None)
            return {
                'subscription_id': subscription_id,
                'approval_url': approve_url
            }, None
        return None, response.text

    def create_order(self, plan_name, final_price, currency="USD", trial_days=None, plan_id=None):
        """
        Creates a PayPal Order or Subscription depending on trial_days.
        Returns the approval link that the frontend should show the user.
        """
        token = self._get_access_token()
        if not token:
            return None, "Authentication Failed"

        # If trial_days is specified, use Subscriptions API
        if trial_days and trial_days > 0:
            # Create product
            product_id, error = self._create_product(token, plan_name)
            if error:
                print(f"[PayPal] Failed to create product: {error}")
                return None, f"Failed to create product: {error}"
            
            # Create billing plan with trial
            billing_plan_id, error = self._create_billing_plan(
                token, product_id, plan_name, final_price, currency, trial_days
            )
            if error:
                print(f"[PayPal] Failed to create billing plan: {error}")
                return None, f"Failed to create billing plan: {error}"
            
            # Create subscription
            result, error = self._create_subscription(token, billing_plan_id, plan_id)
            if error:
                print(f"[PayPal] Failed to create subscription: {error}")
                return None, f"Failed to create subscription: {error}"
            
            return {
                'order_id': result['subscription_id'],
                'approval_url': result['approval_url'],
                'is_subscription': True,
                'is_trial': True
            }, None

        # Standard order-based payment (no trial)
        url = f"{self.base_url}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        # Payload for a basic checkout order
        payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "description": f"Pearto Finance: {plan_name}",
                "amount": {
                    "currency_code": currency,
                    "value": str(final_price)
                }
            }],
            "application_context": {
                "brand_name": "Pearto Finance",
                "return_url": f"{self.return_url}?gateway=paypal&plan_id={plan_id}",
                "cancel_url": self.cancel_url,
                "user_action": "PAY_NOW"
            }
        }

        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            order_id = data.get('id')
            # Extract the 'approve' link for the user
            approve_url = next(link['href'] for link in data['links'] if link['rel'] == 'approve')
            return {
                'order_id': order_id,
                'approval_url': approve_url,
                'is_subscription': False,
                'is_trial': False
            }, None
        else:
            return None, response.text

    def capture_payment(self, order_id):
        """
        Finalizes the transaction after the user approves on PayPal.
        Handles both order-based payments and subscription activations.
        """
        # TESTING BYPASS: Allows testing DB logic without visiting the PayPal site
        if get_setting_secure('PAYPAL_BYPASS_APPROVAL', 'false').lower() == 'true':
            print(f"[DEBUG] Bypassing PayPal Approval for Order: {order_id}")
            return {
                'success': True,
                'transaction_id': f"MOCK_TX_{order_id}",
                'amount': "0.00",
                'is_trial': False
            }, None

        token = self._get_access_token()
        if not token:
            return False, "Authentication Failed"

        # Check if this is a subscription (starts with 'I-')
        if order_id.startswith('I-'):
            return self._capture_subscription(token, order_id)
        else:
            return self._capture_order(token, order_id)

    def _capture_subscription(self, token, subscription_id):
        """Handle subscription activation confirmation."""
        url = f"{self.base_url}/v1/billing/subscriptions/{subscription_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            
            if status in ['ACTIVE', 'APPROVED']:
                # Check if currently in trial
                billing_info = data.get('billing_info', {})
                is_trial = billing_info.get('cycle_executions', [{}])[0].get('tenure_type') == 'TRIAL' if billing_info.get('cycle_executions') else False
                
                return {
                    'success': True,
                    'transaction_id': subscription_id,
                    'amount': 0 if is_trial else billing_info.get('last_payment', {}).get('amount', {}).get('value', '0'),
                    'is_trial': is_trial or status == 'APPROVED'  # New subscriptions with trial start as APPROVED
                }, None
            return False, f"Subscription status: {status}"
        else:
            return False, response.text

    def _capture_order(self, token, order_id):
        """Handle standard order payment capture."""
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }

        response = requests.post(url, headers=headers)
        
        if response.status_code in [200, 201]:
            data = response.json()
            if data.get('status') == 'COMPLETED':
                return {
                    'success': True,
                    'transaction_id': data['purchase_units'][0]['payments']['captures'][0]['id'],
                    'amount': data['purchase_units'][0]['payments']['captures'][0]['amount']['value'],
                    'is_trial': False
                }, None
            return False, f"Payment status: {data.get('status')}"
        else:
            return False, response.text

    def cancel_subscription(self, external_sub_id):
        """
        Cancel a PayPal subscription.
        """
        if not external_sub_id or not external_sub_id.startswith('I-'):
            return True, "Not a subscription - no cancellation needed"
        
        token = self._get_access_token()
        if not token:
            return False, "Authentication Failed"
        
        url = f"{self.base_url}/v1/billing/subscriptions/{external_sub_id}/cancel"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        payload = {
            "reason": "User requested cancellation"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 204:
            return True, "Subscription cancelled successfully"
        else:
            return False, response.text

    def handle_webhook(self, data):
        """
        Logic for processing incoming Webhooks from PayPal.
        Verify headers and update UserSubscription status in DB.
        """
        # We would implement PayPal Webhook Signature verification here
        event_type = data.get('event_type')
        
        # Handle subscription events
        if event_type == 'BILLING.SUBSCRIPTION.ACTIVATED':
            return {'processed': True, 'event': event_type, 'action': 'activate'}
        elif event_type == 'BILLING.SUBSCRIPTION.CANCELLED':
            return {'processed': True, 'event': event_type, 'action': 'cancel'}
        elif event_type == 'BILLING.SUBSCRIPTION.EXPIRED':
            return {'processed': True, 'event': event_type, 'action': 'expire'}
        elif event_type == 'PAYMENT.SALE.COMPLETED':
            return {'processed': True, 'event': event_type, 'action': 'payment'}
        
        return {'processed': True, 'event': event_type}

