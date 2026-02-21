import os
import sys
import uuid
from dotenv import load_dotenv

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models.base import db
from models.settings import Settings
from utils.crypto_utils import encrypt_value

# Load .env file
load_dotenv(override=True)

# List of keys to migrate
KEYS_TO_MIGRATE = [
    {'key': 'JWT_SECRET', 'category': 'general', 'encrypted': True, 'desc': 'JWT Authentication Secret'},
    {'key': 'ADMIN_SECRET_KEY', 'category': 'general', 'encrypted': True, 'desc': 'Admin Panel Secret Key'},
    {'key': 'SMTP_PASS', 'category': 'email', 'encrypted': True, 'desc': 'SMTP Password'},
    {'key': 'ONESIGNAL_APP_ID', 'category': 'marketing', 'encrypted': False, 'desc': 'OneSignal App ID'},
    {'key': 'ONESIGNAL_API_KEY', 'category': 'marketing', 'encrypted': True, 'desc': 'OneSignal API Key'},
    {'key': 'PAYPAL_CLIENT_ID', 'category': 'payment', 'encrypted': False, 'desc': 'PayPal Client ID'},
    {'key': 'PAYPAL_SECRET', 'category': 'payment', 'encrypted': True, 'desc': 'PayPal Secret'},
    {'key': 'STRIPE_SECRET_KEY', 'category': 'payment', 'encrypted': True, 'desc': 'Stripe Secret Key'},
    {'key': 'API_SPORTS_KEY', 'category': 'api_keys', 'encrypted': True, 'desc': 'API-Sports Key'},
]

def migrate():
    app = create_app()
    with app.app_context():
        print("Starting migration of .env keys to database...")
        
        for item in KEYS_TO_MIGRATE:
            key = item['key']
            value = os.getenv(key)
            
            if not value:
                print(f"Skipping {key}: Not found in .env")
                continue
                
            # Check if already exists in DB
            existing = Settings.query.filter_by(key=key).first()
            if existing:
                print(f"Skipping {key}: Already exists in DB")
                continue
                
            # Create new setting
            db_value = value
            if item['encrypted']:
                db_value = encrypt_value(value)
                
            new_setting = Settings(
                id=str(uuid.uuid4()),
                key=key,
                value=db_value,
                category=item['category'],
                description=item['desc'],
                is_encrypted=item['encrypted'],
                is_public=False,
                country_code='GLOBAL'
            )
            
            db.session.add(new_setting)
            print(f"Migrated {key} to database ({'encrypted' if item['encrypted'] else 'plain text'})")
            
        try:
            db.session.commit()
            print("Migration completed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
