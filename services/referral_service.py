"""
Referral Service
PeartoFinance Backend

Handles generation and validation of unique referral codes.
"""

import random
import string
from models import db, User

def generate_unique_referral_code(length=8):
    """
    Generates a unique, easy-to-read referral code.
    Format: PEARTO-XXXXXX
    """
    prefix = "PEARTO-"
    chars = string.ascii_uppercase + string.digits
    
    # Remove ambiguous characters for better readability
    chars = chars.replace('0', '').replace('O', '').replace('I', '').replace('1', '').replace('L', '')
    
    while True:
        suffix = ''.join(random.choices(chars, k=length))
        code = f"{prefix}{suffix}"
        
        # Check if code already exists in database
        exists = User.query.filter_by(referral_code=code).first()
        if not exists:
            return code

def get_user_by_referral_code(code):
    """Finds a user by their referral code"""
    if not code:
        return None
    return User.query.filter_by(referral_code=code).first()
