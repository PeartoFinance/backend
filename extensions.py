"""
Flask Extensions
Centralized initialization to avoid circular imports
"""
from flask_caching import Cache
from flask_compress import Compress

# Initialize extensions without app
cache = Cache()
compress = Compress()
