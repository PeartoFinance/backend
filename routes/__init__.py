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
from .account import account_bp
from .user import user_bp
from .verification import verification_bp
from .devices import devices_bp
from .tools import tools_bp
from .activity import activity_bp
from .pages import pages_bp
from .media import media_bp
from .education import education_bp
from .navigation import navigation_bp
from .news_preferences import news_prefs_bp
from .public_vendors import public_vendors_bp
from .chart import chart_bp
from .subscription import subscription_bp

__all__ = [
    'auth_bp',
    'stocks_bp',
    'crypto_bp',
    'news_bp',
    'geo_bp',
    'market_bp',
    'portfolio_bp',
    'articles_bp',
    'content_bp',
    'account_bp',
    'user_bp',
    'verification_bp',
    'devices_bp',
    'tools_bp',
    'activity_bp',
    'pages_bp',
    'media_bp',
    'education_bp',
    'navigation_bp',
    'news_prefs_bp',
    'public_vendors_bp',
    'chart_bp',
    'subscription_bp',
]
