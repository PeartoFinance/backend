"""
Configuration for Flask backend with SQLAlchemy
"""
import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

# Force load environment variables from .env file, overriding system variables
load_dotenv(override=True)

class Config:
    # Database - SQLAlchemy connection string
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'pearto')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # SQLAlchemy connection string (using PyMySQL)
    # URL-encode password to handle special characters like @, #, etc.
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        # CRITICAL for Shared Hosting: Keep these numbers low to avoid "Too many connections"
        'pool_size': 2,            
        'max_overflow': 0,         # No extra connections beyond pool_size
        'pool_recycle': 30,        # Kill idle connections every 30s (Prevents "MySQL gone away")
        'pool_pre_ping': True,     # Check if connection is alive before using
        'pool_timeout': 10,        # Don't wait too long for a connection
        'pool_reset_on_return': 'rollback',
        'connect_args': {
            'connect_timeout': 5   # Quick failure if DB is unreachable
        }
    }
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key')
    JWT_EXPIRY_HOURS = 24
    
    # Server
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'https://test.pearto.com,https://test.pearto.com').split(',')


config = Config()
