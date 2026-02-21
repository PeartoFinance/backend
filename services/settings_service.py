import os
from models.settings import Settings
from utils.crypto_utils import decrypt_value

from flask import has_app_context

def get_setting_secure(key, default=None):
    """
    Get a setting from the database, falling back to environment variables.
    If the setting is marked as encrypted in the DB, it will be decrypted.
    """
    try:
        # Check if we are inside a Flask application context
        # This prevents "Working outside of application context" errors during startup
        if has_app_context():
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                value = setting.value
                if setting.is_encrypted:
                    value = decrypt_value(value)
                
                # Handle type conversion if needed
                if setting.type == 'boolean':
                    return value.lower() == 'true'
                elif setting.type == 'integer':
                    try:
                        return int(value)
                    except:
                        return default
                return value
    except Exception as e:
        print(f"Error fetching setting {key} from DB: {e}")
    
    # Fallback to environment variables
    return os.getenv(key, default)
