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
        'pool_size': 5,           # Reduced for shared hosting
        'max_overflow': 3,        # Allow a few extra connections
        'pool_recycle': 300,      # Recycle connections every 5 minutes (cPanel MySQL often has short timeouts)
        'pool_pre_ping': True,    # Verify connection before using
        'pool_timeout': 20,       # Connection timeout
        'connect_args': {
            'connect_timeout': 10  # MySQL connect timeout
        }
    }
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key')
    JWT_EXPIRY_HOURS = 24
    
    # Server
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000,https://test.pearto.com').split(',')


config = Config()
