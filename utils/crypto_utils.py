import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def get_cipher():
    """Get Fernet cipher using SETTING_ENCRYPTION_KEY from env"""
    key = os.getenv('SETTING_ENCRYPTION_KEY', 'default-dev-key-change-me-123456789012')
    
    # Ensure key is 32 bytes and base64 encoded for Fernet
    if len(key) < 32:
        # If too short, use PBKDF2 to derive a key
        salt = b'pearto_salt_' # In production, this should be static and secure
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key.encode()))
    elif not key.endswith('='): # Simple check if it might not be b64
        key = base64.urlsafe_b64encode(key[:32].encode())
    
    return Fernet(key)

def encrypt_value(value):
    """Encrypt a string value"""
    if not value:
        return value
    cipher = get_cipher()
    return cipher.encrypt(value.encode()).decode()

def decrypt_value(cipher_text):
    """
    Decrypt a cipher text string using the primary key, 
    falling back to the default key if decryption fails.
    """
    if not cipher_text:
        return cipher_text
        
    # List of keys to try (primary first, then fallback)
    primary_key = os.getenv('SETTING_ENCRYPTION_KEY', 'default-dev-key-change-me-123456789012')
    keys_to_try = [primary_key]
    
    # Always include the default key as a secondary fallback if it's not already primary
    default_dev_key = 'default-dev-key-change-me-123456789012'
    if primary_key != default_dev_key:
        keys_to_try.append(default_dev_key)
        
    for k in keys_to_try:
        try:
            # Re-derive cipher for each key
            temp_key = k
            if len(temp_key) < 32:
                salt = b'pearto_salt_'
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=salt,
                    iterations=100000,
                )
                temp_key = base64.urlsafe_b64encode(kdf.derive(temp_key.encode()))
            elif not temp_key.endswith('='):
                temp_key = base64.urlsafe_b64encode(temp_key[:32].encode())
            else:
                temp_key = temp_key.encode()
                
            cipher = Fernet(temp_key)
            return cipher.decrypt(cipher_text.encode()).decode()
        except Exception:
            continue # Try next key
            
    # If all fail, return as is
    return cipher_text
