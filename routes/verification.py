"""
User Verification API Routes
- Email, phone, and ID verification with badge management
Based on old/Frontend/server/src/verificationApi.js
"""
from flask import Blueprint, request, jsonify
import random
from datetime import datetime
from models import db, User

verification_bp = Blueprint('verification', __name__)

# In-memory store for verification codes (use Redis in production)
verification_codes = {}


def generate_verification_code():
    """Generate 6-digit verification code"""
    return str(random.randint(100000, 999999))


def get_current_user():
    """Helper to get current user from email header"""
    user_email = request.headers.get('X-User-Email')
    if not user_email:
        return None
    return User.query.filter_by(email=user_email).first()


def update_verified_badge(user):
    """Update verified badge based on verification status
    User gets badge when email + at least one other verification
    """
    has_badge = user.email_verified and (user.phone_verified or user.id_verified)
    user.verified_badge = has_badge


@verification_bp.route('/status', methods=['GET'])
def get_verification_status():
    """Get user's verification status"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    return jsonify({
        'emailVerified': user.email_verified or False,
        'emailVerifiedAt': user.email_verified_at.isoformat() if user.email_verified_at else None,
        'phoneVerified': user.phone_verified or False,
        'phoneVerifiedAt': user.phone_verified_at.isoformat() if user.phone_verified_at else None,
        'idVerified': user.id_verified or False,
        'idVerifiedAt': user.id_verified_at.isoformat() if user.id_verified_at else None,
        'verifiedBadge': user.verified_badge or False,
        'hasPhone': bool(user.phone)
    })


@verification_bp.route('/email/send', methods=['POST'])
def send_email_verification():
    """Send email verification code"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Generate verification code
    code = generate_verification_code()
    expires_at = datetime.utcnow().timestamp() + 15 * 60  # 15 minutes
    
    # Store code (in production, use Redis with TTL)
    verification_codes[f'email:{user.email}'] = {
        'code': code,
        'expires_at': expires_at
    }
    
    # In production, send actual email here
    print(f'[VerificationAPI] Email verification code for {user.email}: {code}')
    
    return jsonify({
        'success': True,
        'message': 'Verification code sent to your email',
        # For demo purposes, include code in response
        'demoCode': code
    })


@verification_bp.route('/email/confirm', methods=['POST'])
def confirm_email_verification():
    """Confirm email with verification code"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    code = data.get('code', '')
    
    if not code:
        return jsonify({'error': 'Verification code required'}), 400
    
    # Check code
    stored = verification_codes.get(f'email:{user.email}')
    if not stored:
        return jsonify({'error': 'No verification request found'}), 400
    
    if datetime.utcnow().timestamp() > stored['expires_at']:
        del verification_codes[f'email:{user.email}']
        return jsonify({'error': 'Verification code expired'}), 400
    
    if stored['code'] != code:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    # Mark email as verified
    user.email_verified = True
    user.email_verified_at = datetime.utcnow()
    
    # Update verified badge
    update_verified_badge(user)
    
    db.session.commit()
    
    # Clean up code
    del verification_codes[f'email:{user.email}']
    
    return jsonify({
        'success': True,
        'message': 'Email verified successfully'
    })


@verification_bp.route('/phone/send', methods=['POST'])
def send_phone_verification():
    """Send phone verification code"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    phone = data.get('phone', '')
    
    if not phone:
        return jsonify({'error': 'Phone number required'}), 400
    
    # Update phone number
    user.phone = phone
    db.session.commit()
    
    # Generate verification code
    code = generate_verification_code()
    expires_at = datetime.utcnow().timestamp() + 15 * 60  # 15 minutes
    
    # Store code
    verification_codes[f'phone:{user.email}'] = {
        'code': code,
        'expires_at': expires_at,
        'phone': phone
    }
    
    # In production, send actual SMS here
    print(f'[VerificationAPI] Phone verification code for {phone}: {code}')
    
    return jsonify({
        'success': True,
        'message': 'Verification code sent to your phone',
        # For demo purposes
        'demoCode': code
    })


@verification_bp.route('/phone/confirm', methods=['POST'])
def confirm_phone_verification():
    """Confirm phone with verification code"""
    user = get_current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401
    
    data = request.get_json()
    code = data.get('code', '')
    
    if not code:
        return jsonify({'error': 'Verification code required'}), 400
    
    # Check code
    stored = verification_codes.get(f'phone:{user.email}')
    if not stored:
        return jsonify({'error': 'No verification request found'}), 400
    
    if datetime.utcnow().timestamp() > stored['expires_at']:
        del verification_codes[f'phone:{user.email}']
        return jsonify({'error': 'Verification code expired'}), 400
    
    if stored['code'] != code:
        return jsonify({'error': 'Invalid verification code'}), 400
    
    # Mark phone as verified
    user.phone_verified = True
    user.phone_verified_at = datetime.utcnow()
    
    # Update verified badge
    update_verified_badge(user)
    
    db.session.commit()
    
    # Clean up code
    del verification_codes[f'phone:{user.email}']
    
    return jsonify({
        'success': True,
        'message': 'Phone verified successfully'
    })
