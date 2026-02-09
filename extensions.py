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

# Flask-Limiter: Use Redis in production for thread-safe rate limiting
# Redis URL format: redis://:password@host:port/db
# Production Redis: 127.0.0.1:38469 with password
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'zboeUzOlC2kcjLXWb7v')
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = os.getenv('REDIS_PORT', '38469')
REDIS_DB = os.getenv('REDIS_LIMITER_DB', '0')
REDIS_CACHE_DB = os.getenv('REDIS_CACHE_DB', '1')  # Separate DB for cache

# Build Redis URLs
REDIS_BASE_URL = f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}'
CACHE_REDIS_URL = os.getenv('CACHE_REDIS_URL', f'{REDIS_BASE_URL}/{REDIS_CACHE_DB}')

# Build Redis URL - use Redis if available, fallback to memory
RATELIMIT_STORAGE_URL = os.getenv(
    'RATELIMIT_STORAGE_URL',
    f'redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}'
)

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
