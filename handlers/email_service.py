"""
Email Service
Centralized email handling with template support using Python smtplib
Based on old/Frontend/server/src/services/emailService.js
"""
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import threading
from flask import render_template_string

# Load environment variables
load_dotenv()


# Email configuration from environment
EMAIL_CONFIG = {
    'host': os.getenv('SMTP_HOST', 'smtp.gmail.com'),
    'port': int(os.getenv('SMTP_PORT', '587')),
    'secure': os.getenv('SMTP_SECURE', 'false').lower() == 'true',
    'user': os.getenv('SMTP_USER', ''),
    'password': os.getenv('SMTP_PASS', ''),
    'from_name': os.getenv('EMAIL_FROM_NAME', 'Pearto Finance'),
    'from_address': os.getenv('EMAIL_FROM_ADDRESS', 'noreply@pearto.com'),
}

APP_URL = os.getenv('APP_URL', 'http://localhost:3000')
APP_NAME = 'Pearto Finance'


# ============== EMAIL TEMPLATES ==============

TEMPLATES = {
    'signup': {
        'subject': f'Welcome to {APP_NAME}! 🎉',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">Welcome to {{app_name}}! 🎉</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Thank you for joining {{app_name}}! We're thrilled to have you on board.</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Your account has been successfully created. You can now:</p>
            <ul style="font-size: 16px; color: #333; line-height: 2;">
                <li>Track your investment portfolio</li>
                <li>Get real-time market insights</li>
                <li>Access financial tools and calculators</li>
                <li>Join live webinars and learning sessions</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{login_url}}" style="display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">Get Started</a>
            </div>
            <p style="font-size: 14px; color: #666; line-height: 1.6;">If you have any questions, feel free to reach out to our support team.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This email was sent by {{app_name}}. If you didn't create an account, please ignore this email.</p>
        </div>
    </div>
</body>
</html>''',
        'text': '''Welcome to {{app_name}}!

Hi {{user_name}},

Thank you for joining {{app_name}}! We're thrilled to have you on board.

Your account has been successfully created. You can now:
- Track your investment portfolio
- Get real-time market insights
- Access financial tools and calculators
- Join live webinars and learning sessions

Get started: {{login_url}}

If you have any questions, feel free to reach out to our support team.'''
    },

    'login': {
        'subject': f'New login to your {APP_NAME} account',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: #1a1a2e; border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🔐 Login Notification</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">We noticed a new login to your {{app_name}} account.</p>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 8px 0; color: #555;"><strong>Time:</strong> {{login_time}}</p>
                <p style="margin: 8px 0; color: #555;"><strong>Device:</strong> {{device_info}}</p>
                <p style="margin: 8px 0; color: #555;"><strong>IP Address:</strong> {{ip_address}}</p>
            </div>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">If this was you, no action is needed. If you didn't log in, please secure your account immediately.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{security_url}}" style="display: inline-block; background: #dc3545; color: white; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600;">Secure My Account</a>
            </div>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated security notification from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'text': '''Login Notification

Hi {{user_name}},

We noticed a new login to your {{app_name}} account.

Time: {{login_time}}
Device: {{device_info}}
IP Address: {{ip_address}}

If this was you, no action is needed. If you didn't log in, please secure your account immediately.

Secure your account: {{security_url}}'''
    },

    'forgot_password': {
        'subject': f'Reset your {APP_NAME} password',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">🔑 Password Reset</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">We received a request to reset your password for your {{app_name}} account.</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Click the button below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{reset_url}}" style="display: inline-block; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">Reset Password</a>
            </div>
            <p style="font-size: 14px; color: #666; line-height: 1.6;">This link will expire in <strong>1 hour</strong> for security reasons.</p>
            <p style="font-size: 14px; color: #666; line-height: 1.6;">If you didn't request a password reset, you can safely ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">If the button doesn't work, copy and paste this link:<br><a href="{{reset_url}}" style="color: #667eea;">{{reset_url}}</a></p>
        </div>
    </div>
</body>
</html>''',
        'text': '''Password Reset

Hi {{user_name}},

We received a request to reset your password for your {{app_name}} account.

Click the link below to create a new password:
{{reset_url}}

This link will expire in 1 hour for security reasons.

If you didn't request a password reset, you can safely ignore this email.'''
    },

    'verification_code': {
        'subject': f'Your {APP_NAME} Verification Code',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 28px;">📧 Verify Your Email</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333; line-height: 1.6;">Your verification code is:</p>
            <div style="text-align: center; margin: 30px 0;">
                <div style="background: #f8f9fa; border: 2px dashed #667eea; border-radius: 12px; padding: 30px; display: inline-block;">
                    <span style="font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #667eea;">{{code}}</span>
                </div>
            </div>
            <p style="font-size: 14px; color: #666; line-height: 1.6;">This code will expire in <strong>15 minutes</strong>.</p>
            <p style="font-size: 14px; color: #666; line-height: 1.6;">If you didn't request this code, please ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated message from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'text': '''Verify Your Email

Hi {{user_name}},

Your verification code is: {{code}}

This code will expire in 15 minutes.

If you didn't request this code, please ignore this email.'''
    },

    'profile_update': {
        'subject': f'Your {APP_NAME} Profile Was Updated',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">👤 Profile Updated</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Your profile was updated successfully.</p>
            <div style="background: #f0f9ff; border-left: 4px solid #667eea; padding: 15px; margin: 20px 0;">
                <p style="margin: 0; color: #333;"><strong>Changes:</strong> {{changed_fields}}</p>
            </div>
            <p style="font-size: 14px; color: #666;">If you didn't make these changes, please contact support immediately.</p>
        </div>
    </div>
</body>
</html>''',
        'text': '''Profile Updated

Hi {{user_name}}, your profile was updated.
Changes: {{changed_fields}}

If you didn't make these changes, please contact support.'''
    },

    'google_login': {
        'subject': f'New Google Sign-in to {APP_NAME}',
        'html': '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #4285F4 0%, #34A853 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🔐 Google Sign-in Detected</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Your {{app_name}} account was just accessed via Google Sign-in.</p>
            <div style="background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <p style="margin: 5px 0; color: #555;"><strong>Time:</strong> {{login_time}}</p>
                <p style="margin: 5px 0; color: #555;"><strong>Device:</strong> {{device_info}}</p>
                <p style="margin: 5px 0; color: #555;"><strong>IP:</strong> {{ip_address}}</p>
            </div>
            <p style="font-size: 14px; color: #666;">If this wasn't you, please secure your account immediately.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{security_url}}" style="display: inline-block; background: #dc3545; color: white; text-decoration: none; padding: 12px 28px; border-radius: 8px; font-weight: 600;">Secure My Account</a>
            </div>
        </div>
    </div>
</body>
</html>''',
        'text': '''Google Sign-in Detected

Hi {{user_name}}, your account was accessed via Google.
Time: {{login_time}}
Device: {{device_info}}
IP: {{ip_address}}

If this wasn't you, please secure your account.'''
    },
}


class EmailService:
    """Email service using Python smtplib (similar to PHP mail function)"""
    
    def __init__(self):
        self.config = EMAIL_CONFIG
        self.is_configured = bool(self.config['user'] and self.config['password'])
    
    def _get_smtp_connection(self):
        """Create SMTP connection"""
        if self.config['port'] == 465:
            # SSL connection
            server = smtplib.SMTP_SSL(self.config['host'], self.config['port'])
        else:
            # STARTTLS connection
            server = smtplib.SMTP(self.config['host'], self.config['port'])
            server.starttls()
        
        server.login(self.config['user'], self.config['password'])
        return server
    
    def _render_template(self, template: str, data: Dict[str, Any]) -> str:
        """Replace template variables with actual values using Jinja2"""
        data['app_name'] = APP_NAME
        data['login_url'] = f"{APP_URL}/login"
        data['security_url'] = f"{APP_URL}/profile?tab=devices"
        
        try:
            return render_template_string(template, **data)
        except Exception as e:
            print(f'[EmailService] ❌ Template rendering failed: {e}')
            # Fallback to simple replacement if Flask context is missing or rendering fails
            rendered = template
            for key, value in data.items():
                rendered = rendered.replace('{{' + key + '}}', str(value or ''))
            return rendered

    def send_email_async(self, to: str, template_type: str, data: Dict[str, Any]):
        """Send email in a background thread"""
        thread = threading.Thread(target=self.send_email, args=(to, template_type, data))
        thread.start()

    
    def send_email(self, to: str, template_type: str, data: Dict[str, Any]) -> bool:
        """Send email using template"""
        try:
            template = TEMPLATES.get(template_type)
            if not template:
                print(f'[EmailService] ❌ Unknown template type: {template_type}')
                return False
            
            # Render template
            subject = self._render_template(template['subject'], data.copy())
            html_body = self._render_template(template['html'], data.copy())
            text_body = self._render_template(template['text'], data.copy())
            
            if not self.is_configured:
                # Log email when SMTP not configured (development mode)
                print(f'[EmailService] 📧 Email would be sent (SMTP not configured):')
                print(f'  To: {to}')
                print(f'  Subject: {subject}')
                print(f'  Type: {template_type}')
                return True
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f'{self.config["from_name"]} <{self.config["from_address"]}>'
            msg['To'] = to
            
            # Attach text and HTML parts
            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send email
            with self._get_smtp_connection() as server:
                server.sendmail(self.config['from_address'], to, msg.as_string())
            
            print(f'[EmailService] ✅ Email sent: {template_type} to {to}')
            return True
            
        except Exception as e:
            print(f'[EmailService] ❌ Failed to send {template_type} email: {str(e)}')
            return False
    
    def verify_connection(self) -> Dict[str, Any]:
        """Verify SMTP connection"""
        if not self.is_configured:
            return {'configured': False, 'message': 'SMTP credentials not configured'}
        
        try:
            with self._get_smtp_connection() as server:
                pass
            return {'configured': True, 'message': 'SMTP connection verified'}
        except Exception as e:
            return {'configured': False, 'message': str(e)}


# Create singleton instance
_email_service = EmailService()


# ============== CONVENIENCE FUNCTIONS ==============

def send_welcome_email(user_email: str, user_name: str) -> bool:
    """Send welcome email after signup"""
    return _email_service.send_email_async(user_email, 'signup', {
        'user_name': user_name,
        'user_email': user_email,
    })


def send_login_notification_email(user_email: str, user_name: str, 
                                   ip_address: str = 'Unknown',
                                   user_agent: str = 'Unknown device') -> bool:
    """Send login notification email"""
    return _email_service.send_email_async(user_email, 'login', {
        'user_name': user_name,
        'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'device_info': user_agent[:50] if user_agent else 'Unknown device',
        'ip_address': ip_address,
    })


def send_password_reset_email(user_email: str, user_name: str, reset_token: str) -> bool:
    """Send password reset email"""
    reset_url = f"{APP_URL}/reset-password?token={reset_token}"
    return _email_service.send_email_async(user_email, 'forgot_password', {
        'user_name': user_name,
        'reset_url': reset_url,
    })


def send_verification_code_email(user_email: str, user_name: str, code: str) -> bool:
    """Send email verification code"""
    return _email_service.send_email_async(user_email, 'verification_code', {
        'user_name': user_name,
        'code': code,
    })


def send_profile_update_email(user_email: str, user_name: str, changed_fields: list) -> bool:
    """Send profile update notification email"""
    return _email_service.send_email_async(user_email, 'profile_update', {
        'user_name': user_name,
        'changed_fields': ', '.join(changed_fields) if isinstance(changed_fields, list) else changed_fields,
    })


def send_google_login_email(user_email: str, user_name: str,
                             ip_address: str = 'Unknown',
                             user_agent: str = 'Unknown device') -> bool:
    """Send Google OAuth login notification email"""
    return _email_service.send_email(user_email, 'google_login', {
        'user_name': user_name,
        'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'device_info': user_agent[:50] if user_agent else 'Unknown device',
        'ip_address': ip_address,
    })


def send_phone_verification_sms(phone: str, code: str) -> bool:
    """
    Send phone verification SMS
    Note: This is a placeholder. In production, integrate with:
    - Twilio
    - AWS SNS
    - MessageBird
    - or other SMS gateway
    """
    print(f'[SMSService] 📱 SMS would be sent (SMS gateway not configured):')
    print(f'  To: {phone}')
    print(f'  Code: {code}')
    print(f'  Message: Your Pearto Finance verification code is: {code}')
    return True

