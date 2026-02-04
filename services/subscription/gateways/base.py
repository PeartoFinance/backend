from abc import ABC, abstractmethod

# ==========================================================
# PAYMENT GATEWAY BASE INTERFACE
# Purpose: This file defines the 'Contract' that any payment
# gateway (PayPal, Stripe, etc.) must follow.
# 
# DESIGN CHOICE:
# By using an Abstract Base Class (ABC), we ensure that the rest
# of our app logic doesn't care WHICH gateway is being used.
# If a new developer adds a 'Stripe' gateway, they MUST implement
# these common methods, or the code won't run.
# ==========================================================

class PaymentGateway(ABC):

    @abstractmethod
    def create_order(self, plan, final_price, currency="USD"):
        """
        Initiates a transaction with the provider.
        Should return a URL or Token for the frontend to use.
        """
        pass

    @abstractmethod
    def capture_payment(self, order_id):
        """
        Finalizes the transaction after the user approves it on the gateway side.
        Should return (Success Boolean, Transaction Details).
        """
        pass

    @abstractmethod
    def cancel_subscription(self, external_sub_id):
        """
        Tells the gateway to stop future recurring charges.
        """
        pass

    @abstractmethod
    def handle_webhook(self, data):
        """
        Processes events sent back by the gateway (e.g., 'Recurring payment succeeded').
        """
        pass
