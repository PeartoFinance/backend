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
        # Optimized for stability (Shared Hosting compatible but robust)
        'pool_size': 5,            # Increased from 2 to allow concurrency
        'max_overflow': 10,        # Allow burst connections
        'pool_recycle': 1800,      # Recycle every 30 mins (Standard, 30s was too aggressive)
        'pool_pre_ping': True,     # Check if connection is alive before using
        'pool_timeout': 30,        # Wait longer for a connection if pool is busy
        'pool_reset_on_return': 'rollback',
        'connect_args': {
            'connect_timeout': 10  # More tolerant timeout
        }
    }
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key')
    JWT_EXPIRY_HOURS = 24
    
    # Server
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # API-Sports
    API_SPORTS_KEY = os.getenv('API_SPORTS_KEY', '')
    API_SPORTS_BASE_URL = os.getenv('API_SPORTS_BASE_URL', 'https://v3.football.api-sports.io')



config = Config()
