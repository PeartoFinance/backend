"""
Flask Extensions
Centralized initialization to avoid circular imports
"""
import os
import warnings
from flask_caching import Cache
from flask_compress import Compress
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions without app
cache = Cache()
compress = Compress()

from services.settings_service import get_setting_secure

# Flask-Limiter: Use Redis in production for thread-safe rate limiting
# Redis URL format: redis://:password@host:port/db
# Production Redis: 127.0.0.1:38469 with password
REDIS_PASSWORD = get_setting_secure('REDIS_PASSWORD', '')
REDIS_HOST = get_setting_secure('REDIS_HOST', '127.0.0.1')
REDIS_PORT = get_setting_secure('REDIS_PORT', '38469')
REDIS_DB = get_setting_secure('REDIS_LIMITER_DB', '0')
REDIS_CACHE_DB = get_setting_secure('REDIS_CACHE_DB', '1')  # Separate DB for cache
REDIS_SOCKET_PATH = get_setting_secure('REDIS_SOCKET_PATH', '/home2/ashlya/.redis/redis.sock')
REDIS_USE_SOCKET = str(get_setting_secure('REDIS_USE_SOCKET', 'false')).lower() == 'true'

# Build Redis URLs based on mode
if REDIS_USE_SOCKET:
    # Unix socket URL format for flask-limiter (requires redis+unix://)
    # And redis-py (flask-caching) supports unix://, but we need to be careful.
    # Also, the error "AUTH... without any password configured" implies this socket 
    # does NOT require a password. So we allow omitting it for socket mode.
    
    # Flask-Limiter (limits) requires 'redis+unix://'
    # Redis-py (cache) supports 'unix://'
    # We will construct separate base URLs if needed, or specific full URLs.

    print(f"[Redis] Using Unix Socket: {REDIS_SOCKET_PATH} (No Password)")
    
    # For Flask-Caching (Redis-py): unix://path/to/socket?db=N
    CACHE_REDIS_URL = f'unix://{REDIS_SOCKET_PATH}?db={REDIS_CACHE_DB}'
    
    # For Flask-Limiter: redis+unix:///path/to/socket?db=N
    # Note: explicit slashes might be needed depending on the library version
    RATELIMIT_STORAGE_URL = f'redis+unix://{REDIS_SOCKET_PATH}?db={REDIS_DB}'

else:
    # TCP URL format: redis://[:password@]host:port
    if REDIS_PASSWORD:
        REDIS_BASE_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
    else:
        REDIS_BASE_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'
        
    print(f"[Redis] Using TCP Connection: {REDIS_HOST}:{REDIS_PORT}")
    
    # Configure URLs for TCP
    CACHE_REDIS_URL = get_setting_secure('CACHE_REDIS_URL', f'{REDIS_BASE_URL}/{REDIS_CACHE_DB}')
    RATELIMIT_STORAGE_URL = get_setting_secure('RATELIMIT_STORAGE_URL', f'{REDIS_BASE_URL}/{REDIS_DB}')

# Suppress the production warning when using memory storage intentionally
if RATELIMIT_STORAGE_URL == 'memory://':
    warnings.filterwarnings('ignore', message='.*in-memory storage.*', category=UserWarning)

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=RATELIMIT_STORAGE_URL,
    # Production-friendly rate limits
    default_limits=["5000 per day", "1000 per hour", "100 per minute"],
    storage_options={"socket_connect_timeout": 5},  # Timeout for Redis connection
    strategy="fixed-window",  # Less memory-intensive than moving-window
)
