import requests
import json
import os
from datetime import datetime
from .base import PaymentGateway

# ==========================================================
# PAYPAL ADAPTER
# Purpose: Implements the 'PaymentGateway' interface for PayPal.
# 
# DESIGN CHOICE:
# We use direct 'requests' calls instead of a heavy SDK.
# This makes the code very lightweight and easy to debug.
# All environment variables (CLIENT_ID, SECRET) are loaded
# from '.env' so the developer can use their own sandbox keys.
# ==========================================================

class PayPalGateway(PaymentGateway):
    def __init__(self):
        # We fetch credentials from environment variables for security
        self.client_id = os.getenv('PAYPAL_CLIENT_ID')
        self.secret = os.getenv('PAYPAL_SECRET')
        
        # Determine if we are in Sandbox (testing) or Live mode
        self.mode = os.getenv('PAYPAL_MODE', 'sandbox')
        if self.mode == 'live':
            self.base_url = "https://api-m.paypal.com"
        else:
            self.base_url = "https://api-m.sandbox.paypal.com"

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
        response = requests.post(
            url, 
            auth=(self.client_id, self.secret), 
            headers=headers, 
            data=data
        )
        
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            print(f"[PayPal] Failed to get Access Token: {response.text}")
            return None

    def create_order(self, plan_name, final_price, currency="USD"):
        """
        Creates a PayPal Order. 
        Returns the approval link that the frontend should show the user.
        """
        token = self._get_access_token()
        if not token:
            return None, "Authentication Failed"

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
                "return_url": os.getenv('PAYPAL_RETURN_URL'),
                "cancel_url": os.getenv('PAYPAL_CANCEL_URL'),
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
                'approval_url': approve_url
            }, None
        else:
            return None, response.text

    def capture_payment(self, order_id):
        """
        Finalizes the transaction after the user clicks 'Pay' on PayPal.
        """
        # TESTING BYPASS: Allows testing DB logic without visiting the PayPal site
        if os.getenv('PAYPAL_BYPASS_APPROVAL', 'false').lower() == 'true':
            print(f"[DEBUG] Bypassing PayPal Approval for Order: {order_id}")
            return {
                'success': True,
                'transaction_id': f"MOCK_TX_{order_id}",
                'amount': "0.00" # Simulation amount
            }, None

        token = self._get_access_token()
        if not token:
            return False, "Authentication Failed"

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
                    'amount': data['purchase_units'][0]['payments']['captures'][0]['amount']['value']
                }, None
            return False, f"Payment status: {data.get('status')}"
        else:
            return False, response.text

    def cancel_subscription(self, external_sub_id):
        """
        In this simple helper, legacy 'cancel' isn't needed for single-order intent,
        but for recurring logic, we would call /v1/billing/subscriptions/{id}/cancel
        """
        # Placeholder for full recurring billing logic
        return True, "Order-based payments don't need cancellation"

    def handle_webhook(self, data):
        """
        Logic for processing incoming Webhooks from PayPal.
        Verify headers and update UserSubscription status in DB.
        """
        # We would implement PayPal Webhook Signature verification here
        event_type = data.get('event_type')
        return {'processed': True, 'event': event_type}
