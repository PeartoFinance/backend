"""
Seed Email Templates into Database
Run: source .venv/bin/activate && python seed_email_templates.py
"""
from app import create_app
from models import db, EmailTemplate

# All email templates
TEMPLATES = {
    'signup': {
        'name': 'Welcome Email',
        'subject': 'Welcome to Pearto Finance! 🎉',
        'variables': ['user_name', 'user_email', 'app_name', 'login_url'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 40px; text-align: center;">
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
                <li>Set price alerts for your watchlist</li>
            </ul>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{login_url}}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">Get Started</a>
            </div>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This email was sent by {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''Welcome to {{app_name}}!

Hi {{user_name}},

Thank you for joining {{app_name}}! We're thrilled to have you on board.

Your account has been successfully created. You can now:
- Track your investment portfolio
- Get real-time market insights
- Access financial tools and calculators
- Set price alerts for your watchlist

Get started: {{login_url}}'''
    },

    'login': {
        'name': 'Login Notification',
        'subject': 'New login to your Pearto Finance account',
        'variables': ['user_name', 'login_time', 'device_info', 'ip_address', 'security_url', 'app_name'],
        'body_html': '''<!DOCTYPE html>
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
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">We noticed a new login to your Pearto Finance account.</p>
            <div style="background: #f0f9ff; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0;">
                <p style="margin: 5px 0;"><strong>Time:</strong> {{login_time}}</p>
                <p style="margin: 5px 0;"><strong>Device:</strong> {{device_info}}</p>
                <p style="margin: 5px 0;"><strong>IP Address:</strong> {{ip_address}}</p>
            </div>
            <p style="font-size: 14px; color: #666;">If this was you, no action is needed. If you didn't log in, please secure your account immediately.</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{security_url}}" style="display: inline-block; background: #dc2626; color: white; text-decoration: none; padding: 12px 24px; border-radius: 8px; font-weight: 600;">Secure My Account</a>
            </div>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated security notification from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''Login Notification

Hi {{user_name}},

We noticed a new login to your Pearto Finance account.

Time: {{login_time}}
Device: {{device_info}}
IP: {{ip_address}}

If this was you, no action is needed. If you didn't log in, please secure your account.'''
    },

    'price_alert': {
        'name': 'Price Alert',
        'subject': '🎯 {{symbol}} Price Alert - Target Reached!',
        'variables': ['user_name', 'symbol', 'current_price', 'target_price', 'direction', 'app_name', 'dashboard_url'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🎯 Price Alert Triggered!</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Your price alert for <strong>{{symbol}}</strong> has been triggered!</p>
            
            <div style="background: #f0fdf4; border: 2px solid #10b981; border-radius: 12px; padding: 25px; margin: 25px 0; text-align: center;">
                <div style="font-size: 32px; font-weight: bold; color: #059669;">{{symbol}}</div>
                <div style="font-size: 42px; font-weight: bold; color: #111; margin: 10px 0;">${{current_price}}</div>
                <div style="font-size: 14px; color: #666;">Target: ${{target_price}} ({{direction}})</div>
            </div>
            
            <p style="font-size: 14px; color: #666;">This alert will not trigger again. Create a new alert if you want to track this stock further.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{dashboard_url}}" style="display: inline-block; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">View Dashboard</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">You're receiving this because you set a price alert on {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''🎯 Price Alert Triggered!

Hi {{user_name}},

Your price alert for {{symbol}} has been triggered!

{{symbol}}: ${{current_price}}
Target: ${{target_price}} ({{direction}})

This alert will not trigger again. Create a new alert if you want to track this stock further.

View Dashboard: {{dashboard_url}}'''
    },

    'password_reset': {
        'name': 'Password Reset',
        'subject': 'Reset Your Pearto Finance Password',
        'variables': ['user_name', 'reset_url', 'reset_code', 'app_name'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: #1a1a2e; border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">🔑 Password Reset</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{reset_url}}" style="display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 16px;">Reset Password</a>
            </div>
            <p style="font-size: 14px; color: #666;">Or use this code: <strong>{{reset_code}}</strong></p>
            <p style="font-size: 14px; color: #666;">This link expires in 15 minutes. If you didn't request this, ignore this email.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated message from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''Password Reset

Hi {{user_name}},

We received a request to reset your password.

Reset your password: {{reset_url}}
Or use code: {{reset_code}}

This link expires in 15 minutes. If you didn't request this, ignore this email.'''
    },

    'verification': {
        'name': 'Email Verification',
        'subject': 'Verify Your Email - Pearto Finance',
        'variables': ['user_name', 'code', 'app_name'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">✉️ Verify Your Email</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Please use the following code to verify your email address:</p>
            <div style="text-align: center; margin: 30px 0;">
                <div style="display: inline-block; background: #f0fdf4; border: 2px dashed #10b981; padding: 20px 40px; border-radius: 12px;">
                    <span style="font-size: 36px; font-weight: bold; color: #059669; letter-spacing: 8px;">{{code}}</span>
                </div>
            </div>
            <p style="font-size: 14px; color: #666;">This code expires in 15 minutes.</p>
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">This is an automated message from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''Verify Your Email

Hi {{user_name}},

Your verification code is: {{code}}

This code expires in 15 minutes.'''
    },

    'daily_digest': {
        'name': 'Daily Market Digest',
        'subject': '📊 Your Daily Market Digest',
        'variables': ['user_name', 'date', 'gainers_count', 'losers_count', 'top_gainer', 'top_loser', 'market_summary', 'dashboard_url', 'app_name'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📊 Daily Market Digest</h1>
            <p style="color: #94a3b8; margin-top: 10px;">{{date}}</p>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Here's your daily summary:</p>
            
            <div style="display: flex; gap: 15px; margin: 25px 0;">
                <div style="flex: 1; background: #f0fdf4; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #10b981;">📈 {{gainers_count}}</div>
                    <div style="font-size: 12px; color: #666;">Gainers</div>
                </div>
                <div style="flex: 1; background: #fef2f2; padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 28px; font-weight: bold; color: #ef4444;">📉 {{losers_count}}</div>
                    <div style="font-size: 12px; color: #666;">Losers</div>
                </div>
            </div>
            
            <p style="font-size: 14px; color: #666;">{{market_summary}}</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{dashboard_url}}" style="display: inline-block; background: #10b981; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600;">View Full Report</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">You're subscribed to daily digests from {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''📊 Daily Market Digest - {{date}}

Hi {{user_name}},

Here's your daily summary:

📈 Gainers: {{gainers_count}}
📉 Losers: {{losers_count}}

{{market_summary}}

View full report: {{dashboard_url}}'''
    },

    'earnings_reminder': {
        'name': 'Earnings Reminder',
        'subject': '📅 Earnings Tomorrow: {{symbols}}',
        'variables': ['user_name', 'symbols', 'earnings_count', 'dashboard_url', 'app_name'],
        'body_html': '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7fa; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;">
    <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
        <div style="background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); border-radius: 16px 16px 0 0; padding: 30px; text-align: center;">
            <h1 style="color: white; margin: 0; font-size: 24px;">📅 Earnings Tomorrow</h1>
        </div>
        <div style="background: white; padding: 40px; border-radius: 0 0 16px 16px;">
            <p style="font-size: 16px; color: #333;">Hi {{user_name}},</p>
            <p style="font-size: 16px; color: #333;">Companies on your watchlist are reporting earnings tomorrow:</p>
            
            <div style="background: #fffbeb; border: 1px solid #f59e0b; border-radius: 8px; padding: 20px; margin: 20px 0; text-align: center;">
                <div style="font-size: 18px; font-weight: bold; color: #92400e;">{{symbols}}</div>
            </div>
            
            <p style="font-size: 14px; color: #666;">Earnings announcements can cause significant price movements. Stay informed!</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{{dashboard_url}}" style="display: inline-block; background: #f59e0b; color: white; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600;">View Calendar</a>
            </div>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            <p style="font-size: 12px; color: #999; text-align: center;">You're receiving this because you have earnings alerts enabled on {{app_name}}.</p>
        </div>
    </div>
</body>
</html>''',
        'body_text': '''📅 Earnings Tomorrow

Hi {{user_name}},

Companies on your watchlist are reporting earnings tomorrow:

{{symbols}}

Earnings announcements can cause significant price movements. Stay informed!

View Calendar: {{dashboard_url}}'''
    },
}


def seed_templates():
    app = create_app()
    with app.app_context():
        count = 0
        for template_id, data in TEMPLATES.items():
            existing = EmailTemplate.query.get(template_id)
            if existing:
                # Update existing
                existing.name = data['name']
                existing.subject = data['subject']
                existing.body_html = data['body_html']
                existing.body_text = data['body_text']
                existing.variables = data['variables']
                existing.is_active = True
                print(f"  Updated: {template_id}")
            else:
                # Create new
                template = EmailTemplate(
                    id=template_id,
                    name=data['name'],
                    subject=data['subject'],
                    body_html=data['body_html'],
                    body_text=data['body_text'],
                    variables=data['variables'],
                    is_active=True
                )
                db.session.add(template)
                print(f"  Created: {template_id}")
            count += 1
        
        db.session.commit()
        print(f"\n✓ Seeded {count} email templates")


if __name__ == '__main__':
    seed_templates()
