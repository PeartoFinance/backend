import os
from .paypal import PayPalGateway

# ==========================================================
# PAYMENT GATEWAY FACTORY
# Purpose: This is the 'Switch' that selects the active gateway.
# 
# DESIGN CHOICE:
# Instead of hardcoding 'PayPal' across the app, we ask the 
# factory for the active gateway. If we switch to 'Stripe' 
# in the future, we only add it here.
# ==========================================================

def get_payment_gateway():
    """
    Returns an instance of the active payment gateway based on .env
    """
    gateway_type = os.getenv('ACTIVE_PAYMENT_GATEWAY', 'paypal').lower()

    if gateway_type == 'paypal':
        return PayPalGateway()
    
    # Placeholder for future gateways
    # elif gateway_type == 'stripe':
    #     return StripeGateway()

    raise ValueError(f"Unsupported or unconfigured payment gateway: {gateway_type}")
