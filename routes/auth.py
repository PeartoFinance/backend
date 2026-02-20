"""
Authentication API Routes
- Login, signup, password reset with SQLAlchemy
- Email notifications for login, signup, password reset
"""
from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import uuid
from datetime import datetime, timedelta, timezone
from config import config
from models import db, User, PasswordResetToken, UserProfile
from handlers import send_welcome_email, send_login_notification_email, send_password_reset_email, track_login, track_signup
from models.user import UserSession
from utils.device import parse_user_agent
from .decorators import auth_required
import os
from google.oauth2 import id_token
from google.auth.transport import requests


auth_bp = Blueprint('auth', __name__)


def _get_client_ip() -> str:
    """Extract the real client IP from proxy headers, safe for VARCHAR(45)."""
    ip = (
        request.headers.get('X-Forwarded-For', '').split(',')[0].strip()
        or request.headers.get('X-Real-IP')
        or request.remote_addr
        or 'Unknown'
    )
    return ip[:45]


@auth_bp.route('/login', methods=['POST'])
def login():
    """Login with email and password"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    # check account status
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Check account status
    if user.account_status == 'deleted':
        return jsonify({'error': 'This account has been permanently deleted.'}), 403
    
    if user.account_status == 'deactivated':
        return jsonify({'error': 'Account is deactivated. Please reactivate to login.'}), 403
    
    if user.account_status == 'suspended':
        return jsonify({'error': 'Account is suspended. Please contact support.'}), 403
    
    # Check if user has a password (Google OAuth users have empty password)
    if not user.password:
        return jsonify({'error': 'Please sign in with Google'}), 400
    
    # Verify password
    try:
        if not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
            return jsonify({'error': 'Invalid credentials'}), 401
    except ValueError:
        # Invalid bcrypt hash (e.g., empty or malformed password)
        return jsonify({'error': 'Please sign in with Google'}), 400
    
    # Generate JWT token
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS)
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm='HS256')
    
    # Update last login
    user.last_login_at = datetime.now(timezone.utc)
    
    # Create/Update session
    if isinstance(token, bytes):
        token = token.decode('utf-8')
        
    # Clear old sessions
    UserSession.query.filter_by(user_id=user.id).delete()
    
    # Create new session
    session = UserSession(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS),
        ip_address=_get_client_ip(),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(session)
    db.session.commit()
    
    # Track login activity
    try:
        ip_address = _get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown device')
        track_login(user.id, success=True, method='email', ip=ip_address)
        
        # Check user preferences before sending login notification
        from services.preference_checker import should_send_notification
        if should_send_notification(user.id, 'security', 'email'):
            friendly_device = parse_user_agent(user_agent)
            send_login_notification_email(user.email, user.name, ip_address, friendly_device)
    except Exception as e:
        print(f'[Auth] Login notification failed: {e}')
    
    return jsonify({
        'user': user.to_dict(),
        'token': token
    })


@auth_bp.route('/signup', methods=['POST'])
def signup():
    """Register a new user"""
    data = request.get_json()
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    referral_code_input = data.get('referralCode', '').strip()
    country_code = request.user_country
    
    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Check if email already exists
    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Check referral code if provided
    referred_by_id = None
    if referral_code_input:
        from services.referral_service import get_user_by_referral_code
        referrer = get_user_by_referral_code(referral_code_input)
        if referrer:
            referred_by_id = referrer.id
            print(f"[Referral] User {email} referred by {referrer.email}")
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Generate unique referral code for the new user
    from services.referral_service import generate_unique_referral_code
    new_user_referral_code = generate_unique_referral_code()
    
    # Create user (id is auto-generated by database)
    user = User(
        name=name,
        email=email,
        password=password_hash,
        role='user',
        country_code=country_code,
        referral_code=new_user_referral_code,
        referred_by=referred_by_id
    )
    
    db.session.add(user)
    db.session.commit()
    
    # Create user profile automatically
    profile = UserProfile(
        user_id=user.id,
        profile_visibility='public',
        trading_style='mixed'
    )
    db.session.add(profile)
    db.session.commit()
    
    # NEW: Automatically grant 'Free' subscription (if plan exists)
    try:
        from models.subscription import SubscriptionPlan
        from services.subscription.manager import SubscriptionManager
        free_plan = SubscriptionPlan.query.filter_by(name='Free', is_active=True).first()
        if free_plan:
            SubscriptionManager.activate_subscription(user.id, free_plan.id, gateway='system')
            print(f"[Subscription] Free plan auto-assigned to {email}")
    except Exception as e:
        print(f"[Subscription] Auto-assignment failed: {e}")
    
    # Track signup activity and send welcome email
    try:
        ip_address = _get_client_ip()
        track_signup(user.id, method='email', ip=ip_address)
        
        # Always send welcome email for new users
        send_welcome_email(user.email, user.name)
    except Exception as e:
        print(f'[Auth] Signup tracking/email failed: {e}')
    
    return jsonify(user.to_dict()), 201


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Request password reset"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'error': 'Email required'}), 400
    
    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    # Always return success to prevent email enumeration
    if user:
        token_value = str(uuid.uuid4())
        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token_value,
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
        )
        db.session.add(reset_token)
        db.session.commit()
        
        # Send password reset email
        try:
            send_password_reset_email(user.email, user.name, token_value)
        except Exception as e:
            print(f'[Auth] Password reset email failed: {e}')
    
    return jsonify({'message': 'If email exists, reset link will be sent'})


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('password', '')
    
    if not token or not new_password:
        return jsonify({'error': 'Token and password required'}), 400
    
    if len(new_password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Find valid token
    reset_token = PasswordResetToken.query.filter(
        PasswordResetToken.token == token,
        PasswordResetToken.expires_at > datetime.now(timezone.utc),
        PasswordResetToken.used == False
    ).first()
    
    if not reset_token:
        return jsonify({'error': 'Invalid or expired token'}), 400
    
    # Update password
    user = User.query.get(reset_token.user_id)
    if user:
        user.password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        reset_token.used = True
        # Invalidate all active sessions so everyone must re-login with new password
        UserSession.query.filter_by(user_id=user.id).delete()
        db.session.commit()
    
    return jsonify({'message': 'Password reset successful'})


@auth_bp.route('/me', methods=['GET'])
@auth_required
def get_current_user():
    """Get current user from token"""
    return jsonify(request.user.to_dict())


@auth_bp.route('/google-signin', methods=['POST'])
def google_signin():
    """Login or signup with Google OAuth (syncs with Firebase)"""
    from handlers import send_google_login_email
    
    data = request.get_json()
    id_token_str = data.get('idToken') # Secure: Receive token from frontend

    referral_code_input = data.get('referralCode', '').strip()

    if not id_token_str:
        return jsonify({'error': 'Firebase ID Token required'}), 400

    try:
         # Verify Firebase ID Token to prevent account spoofing
        # Firebase tokens use a different certificate URL than standard Google tokens
        firebase_project_id = os.getenv('FIREBASE_PROJECT_ID')
        certs_url = 'https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com'
        
        idinfo = id_token.verify_token(
            id_token_str, 
            requests.Request(), 
            audience=firebase_project_id,
            certs_url=certs_url
        )
        
        email = idinfo['email'].lower()
        name = idinfo.get('name')
        avatar_url = idinfo.get('picture')
        firebase_uid = idinfo.get('sub')
    except Exception as e:
        print(f'[Auth] Firebase token verification failed: {e}')
        return jsonify({'error': 'Invalid Firebase Token'}), 401

    # Check if user exists
    user = User.query.filter_by(email=email).first()
    
    if user:
        # Check account status
        if user.account_status == 'deleted':
            return jsonify({'error': 'This account has been permanently deleted.'}), 403
        
        if user.account_status == 'deactivated':
            return jsonify({'error': 'Account is deactivated. Please reactivate to login.'}), 403
        
        if user.account_status == 'suspended':
            return jsonify({'error': 'Account is suspended. Please contact support.'}), 403

        # Existing user - update Google/Firebase info if needed
        if firebase_uid and not user.firebase_uid:
            user.firebase_uid = firebase_uid
        if avatar_url and not user.avatar_url:
            user.avatar_url = avatar_url
        
        user.last_login_at = datetime.now(timezone.utc)
        db.session.commit()
        
    else:
        # Check referral code if provided
        referred_by_id = None
        if referral_code_input:
            from services.referral_service import get_user_by_referral_code
            referrer = get_user_by_referral_code(referral_code_input)
            if referrer:
                referred_by_id = referrer.id
                print(f"[Referral] Google User {email} referred by {referrer.email}")

        # Generate unique referral code for the new user
        from services.referral_service import generate_unique_referral_code
        new_user_referral_code = generate_unique_referral_code()

        # New user - create account
        user = User(
            name=name or email.split('@')[0],
            email=email,
            password='',  # No password for Google users
            role='user',
            firebase_uid=firebase_uid,
            avatar_url=avatar_url,
            email_verified=True,  # Google verified
            email_verified_at=datetime.now(timezone.utc),
            country_code=request.user_country,
            referral_code=new_user_referral_code,
            referred_by=referred_by_id
        )
        db.session.add(user)
        db.session.commit()
        
        # Create user profile automatically
        profile = UserProfile(
            user_id=user.id,
            profile_visibility='public',
            trading_style='mixed'
        )
        db.session.add(profile)
        db.session.commit()
        
        # NEW: Automatically grant 'Free' subscription (if plan exists) for Google Signup
        try:
            from models.subscription import SubscriptionPlan
            from services.subscription.manager import SubscriptionManager
            free_plan = SubscriptionPlan.query.filter_by(name='Free', is_active=True).first()
            if free_plan:
                SubscriptionManager.activate_subscription(user.id, free_plan.id, gateway='system')
                print(f"[Subscription] Free plan auto-assigned to {email}")
        except Exception as e:
            print(f"[Subscription] Auto-assignment failed: {e}")

        
                
        # Send welcome email for new users
        try:
            send_welcome_email(user.email, user.name)
        except Exception as e:
            print(f'[Auth] Welcome email failed: {e}')

        # Track signup activity
        try:
            ip_address = _get_client_ip()
            track_signup(user.id, method='google', ip=ip_address)
        except Exception as e:
            print(f'[Auth] Signup tracking failed: {e}')
    
    # Generate JWT token
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS)
    }
    token = jwt.encode(payload, config.JWT_SECRET, algorithm='HS256')

    # normalize token
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    
    UserSession.query.filter_by(user_id=user.id).delete()

    # create session
    session = UserSession(
        user_id=user.id,
        token=token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS)
    )
    db.session.add(session)
    db.session.commit()


    # Track login and send notification
    try:
        ip_address = _get_client_ip()
        user_agent = request.headers.get('User-Agent', 'Unknown device')
        
        # Track login
        track_login(user.id, success=True, method='google', ip=ip_address)
        
        from services.preference_checker import should_send_notification
        if should_send_notification(user.id, 'security', 'email'):
            friendly_device = parse_user_agent(user_agent)
            send_google_login_email(user.email, user.name, ip_address, friendly_device)
    except Exception as e:
        print(f'[Auth] Google login email failed: {e}')
    
    return jsonify({
        'user': user.to_dict(),
        'token': token
    })


@auth_bp.route('/logout', methods=['POST'])
@auth_required
def logout():
    """
    Logout the current user by destroying their session in the DB.
    This prevents 'ghost sessions' and improves security.
    """
    try:
        # User is already identified by @auth_required
        auth_header = request.headers.get('Authorization', '')
        token = auth_header.split(' ')[1] if ' ' in auth_header else None

        if token:
            UserSession.query.filter_by(user_id=request.user.id, token=token).delete()
            db.session.commit()
            
        return jsonify({'success': True, 'message': 'Logged out successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# set password for google user
@auth_bp.route('/set-password', methods=['POST'])
@auth_required
def set_password():
    """Set password for Google user"""
    user = request.user
    data = request.get_json()
    password = data.get('password')

    if user.password:
        return jsonify({'error': 'Password already set'}), 400

    if not password or len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters'}), 400

    user.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    # Invalidate all active sessions so everyone must re-login with new password
    UserSession.query.filter_by(user_id=user.id).delete()
    
    # Create a new session for the current user so they stay logged in
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'exp': datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS)
    }
    new_token = jwt.encode(payload, config.JWT_SECRET, algorithm='HS256')
    if isinstance(new_token, bytes):
        new_token = new_token.decode('utf-8')
    
    new_session = UserSession(
        user_id=user.id,
        token=new_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=config.JWT_EXPIRY_HOURS),
        ip_address=_get_client_ip(),
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(new_session)
    db.session.commit()
    
    # Track password change/set
    try:
        from handlers import track_password_change
        track_password_change(user.id, _get_client_ip())
    except Exception as e:
        print(f'[Auth] Failed to track password set: {e}')

    return jsonify({'message': 'Password set successfully', 'token': new_token})