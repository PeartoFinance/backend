import os
from models.settings import Settings
from utils.crypto_utils import decrypt_value

from flask import has_app_context

def get_setting_secure(key, default=None):
    """
    Get a setting from the database, falling back to environment variables.
    Handles multiple layers of encryption if present.
    """
    try:
        # Check if we are inside a Flask application context
        if has_app_context():
            setting = Settings.query.filter_by(key=key).first()
            if setting:
                value = setting.value
                
                # Recursive decryption for cases of double-encryption or wrapping
                # Limited to 3 iterations to prevent infinite loops on junk data
                iterations = 0
                while isinstance(value, str) and value.startswith('gAAAA') and iterations < 3:
                    decrypted = decrypt_value(value)
                    if decrypted == value: # Decryption failed or returned same value
                        break
                    value = decrypted
                    iterations += 1
                
                # Handle type conversion
                if setting.type == 'boolean':
                    return str(value).lower() == 'true'
                elif setting.type == 'integer':
                    try:
                        return int(value)
                    except:
                        return default
                return value
    except Exception as e:
        print(f"Error fetching setting {key} from DB: {e}")
    
    # Fallback to environment variables
    val = os.getenv(key, default)
    
    # Even if from Env, try to decrypt if it looks like a Fernet token
    iterations = 0
    while isinstance(val, str) and val.startswith('gAAAA') and iterations < 3:
        decrypted = decrypt_value(val)
        if decrypted == val:
            break
        val = decrypted
        iterations += 1
            
    return val
