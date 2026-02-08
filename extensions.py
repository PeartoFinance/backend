"""
Flask Extensions
Centralized initialization to avoid circular imports
"""
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions without app
cache = Cache()
compress = Compress()
limiter = Limiter(key_func=get_remote_address)
