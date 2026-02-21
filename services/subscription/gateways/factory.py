import os
from services.settings_service import get_setting_secure
from .paypal import PayPalGateway
from .stripe import StripeGateway

# ==========================================================
# PAYMENT GATEWAY FACTORY
# Purpose: This is the 'Switch' that selects the active gateway.
# 
# DESIGN CHOICE:
# Accepts gateway_type as parameter for user-selectable gateways.
# Falls back to ACTIVE_PAYMENT_GATEWAY env var if not specified.
# ==========================================================

def get_payment_gateway(gateway_type=None):
    """
    Returns an instance of the requested payment gateway.
    
    Args:
        gateway_type: 'paypal' or 'stripe'. If None, uses env var.
    """
    gateway_type = (gateway_type or get_setting_secure('ACTIVE_PAYMENT_GATEWAY', 'paypal')).lower()

    if gateway_type == 'paypal':
        return PayPalGateway()
    elif gateway_type == 'stripe':
        return StripeGateway()

    raise ValueError(f"Unsupported payment gateway: {gateway_type}")

