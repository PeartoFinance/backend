"""
Routes package initialization
"""
from .auth import auth_bp
from .stocks import stocks_bp
from .crypto import crypto_bp
from .news import news_bp
from .geo import geo_bp
from .market import market_bp
from .portfolio import portfolio_bp
from .articles import articles_bp
from .content import content_bp

__all__ = [
    'auth_bp', 
    'stocks_bp', 
    'crypto_bp', 
    'news_bp', 
    'geo_bp',
    'market_bp',
    'portfolio_bp',
    'articles_bp',
    'content_bp'
]
