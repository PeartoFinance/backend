"""
Configuration for Flask backend with SQLAlchemy
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Database - SQLAlchemy connection string
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'pearto')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # SQLAlchemy connection string (using PyMySQL)
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        "?charset=utf8mb4"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }
    
    # JWT
    JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key')
    JWT_EXPIRY_HOURS = 24
    
    # Server
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    # CORS
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')


config = Config()
