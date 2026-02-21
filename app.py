"""
Flask Backend - Main Application
PeartoFinance API Server with SQLAlchemy
"""
import os
# Limit OpenBLAS/NumPy threads to prevent resource exhaustion on shared hosting
# MUST be set before importing numpy or any library that uses it (yfinance, pandas, etc.)
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['MKL_NUM_THREADS'] = '1'
os.environ['NUMEXPR_NUM_THREADS'] = '1'
os.environ['OMP_NUM_THREADS'] = '1'

# Patch yfinance BEFORE importing anything else that might check for SQLite
try:
    import patch_yfinance
except ImportError:
    pass

from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
from services.settings_service import get_setting_secure
from models.base import db
from flask_migrate import Migrate
from extensions import cache, compress, limiter, CACHE_REDIS_URL

# Initialize Flask app
app = Flask(__name__)

# [PROD FIX] Enable ProxyFix to get the REAL client IP when running behind 
# a reverse proxy (like Nginx, Gunicorn, or Cloudflare). 
# Without this, all users appear to have the same IP, which breaks rate limiting.
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)

# Load configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS

# Cache configuration - Redis for shared caching across workers
# Falls back to simple cache if Redis is unavailable
try:
    import redis
    r = redis.from_url(CACHE_REDIS_URL)
    r.ping()  # Test connection
    app.config['CACHE_TYPE'] = 'redis'
    app.config['CACHE_REDIS_URL'] = CACHE_REDIS_URL
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    print("[OK] Using Redis cache backend")
except Exception as e:
    print(f"[WARNING] Redis cache unavailable, using simple cache: {e}")
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 30

# Initialize extensions
db.init_app(app)
cache.init_app(app)
compress.init_app(app)  # Auto-compress responses > 500 bytes
limiter.init_app(app)   # Initialize rate limiting

# For migration
migrate = Migrate(app, db)

# Import all models so Alembic can detect them during migration
import models


# Configure CORS - explicitly list all allowed origins (cannot use * with credentials)
import re

# Configure CORS - use regex for local network IPs to avoid "PreflightMissingAllowOriginHeader"
CORS(app, 
     origins=[
         "http://localhost:3000",
         "http://localhost:3001",
         "http://127.0.0.1:3000",
         "https://pearto.com",
         "https://www.pearto.com",
         "https://stocks.pearto.com",
         "https://pearto.com",
         "https://frontend-admin-pearto.vercel.app",
         "https://stocks-nine-blush.vercel.app",
         re.compile(r"^http://192\.168\.\d{1,3}\.\d{1,3}:\d{1,5}$"),  # Matches any local IP
         re.compile(r"^http://127\.0\.0\.1:\d{1,5}$"),               # Matches localhost with any port
     ],
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Admin-Secret", "X-Admin-Country", "X-User-Country", "X-User-Email", "X-Session-Token"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization", "Content-Disposition"])


# Middleware to extract country from headers
@app.before_request
def extract_country():
    """Extract user country from headers (admin or user)"""
    # Admin routes use X-Admin-Country, user routes use X-User-Country
    request.user_country = (
        request.headers.get('X-Admin-Country') or
        request.headers.get('X-User-Country')
    )


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'service': 'PeartoFinance API',
        'version': '1.0.0'
    })


# Import and register blueprints after app initialization
from routes.auth import auth_bp
from routes.stocks import stocks_bp
from routes.crypto import crypto_bp
from routes.news import news_bp
from routes.geo import geo_bp
from routes.market import market_bp
from routes.portfolio import portfolio_bp
from routes.articles import articles_bp
from routes.content import content_bp
from routes.account import account_bp
from routes.user import user_bp
from routes.verification import verification_bp
from routes.devices import devices_bp
from routes.tools import tools_bp
from routes.admin import admin_bp
from routes.activity import activity_bp
from routes.pages import pages_bp
from routes.media import media_bp
from routes.education import education_bp
from routes.ai import ai_bp
from routes.jobs import jobs_bp
from routes.navigation import navigation_bp
from routes.social import social_bp
from routes.backup import backup_bp
from routes.news_preferences import news_prefs_bp
from routes.currency import currency_bp
from routes.subscription import subscription_bp
from routes.glossary import glossary_bp
from routes.help_public import help_public_bp
from routes.developer import developer_bp
from routes.public_v1 import public_v1_bp


app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(stocks_bp, url_prefix='/api/stocks')
app.register_blueprint(crypto_bp, url_prefix='/api/crypto')
app.register_blueprint(news_bp, url_prefix='/api/news')
app.register_blueprint(geo_bp, url_prefix='/api')
app.register_blueprint(market_bp, url_prefix='/api/market')
app.register_blueprint(portfolio_bp, url_prefix='/api/portfolio')
app.register_blueprint(articles_bp, url_prefix='/api/articles')
app.register_blueprint(content_bp, url_prefix='/api/content')
app.register_blueprint(account_bp, url_prefix='/api/account')
app.register_blueprint(user_bp, url_prefix='/api/user')
app.register_blueprint(verification_bp, url_prefix='/api/user/verification')
app.register_blueprint(devices_bp, url_prefix='/api/devices')
app.register_blueprint(tools_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(activity_bp, url_prefix='/api')
app.register_blueprint(pages_bp, url_prefix='/api')
app.register_blueprint(media_bp)
app.register_blueprint(education_bp, url_prefix='/api/education')
app.register_blueprint(ai_bp, url_prefix='/api/ai')
app.register_blueprint(jobs_bp, url_prefix='/api/admin/jobs')
app.register_blueprint(navigation_bp, url_prefix='/api')
app.register_blueprint(social_bp, url_prefix='/api/social')
app.register_blueprint(backup_bp, url_prefix='/api/backup')
app.register_blueprint(currency_bp)
app.register_blueprint(subscription_bp, url_prefix='/api/subscription')
app.register_blueprint(glossary_bp, url_prefix='/api')
app.register_blueprint(help_public_bp, url_prefix='/api')
app.register_blueprint(developer_bp, url_prefix='/api/developer')
app.register_blueprint(public_v1_bp, url_prefix='/api/v1/public')

from routes.sports import sports_bp
app.register_blueprint(sports_bp, url_prefix='/api/sports')

from routes.sports_settings import sports_settings_bp
app.register_blueprint(sports_settings_bp, url_prefix='/api/admin/sports-settings')

# User feature routes
from routes.alerts import alerts_bp
from routes.documents import documents_bp
app.register_blueprint(alerts_bp, url_prefix='/api/user/alerts')
app.register_blueprint(documents_bp, url_prefix='/api/user/documents')
app.register_blueprint(news_prefs_bp, url_prefix='/api/user/news-preferences')

# Public Vendor Routes
from routes.public_vendors import public_vendors_bp
app.register_blueprint(public_vendors_bp)

# Chart routes (drawings, templates, indicators, analysis)
from routes.chart import chart_bp
app.register_blueprint(chart_bp, url_prefix='/api/chart')

# Cron routes for external cURL calls (cPanel)
from routes.cron import cron_bp
app.register_blueprint(cron_bp, url_prefix='/api/cron')

# Market status routes (market hours, open/close status)
from routes.market_status import market_status_bp

app.register_blueprint(market_status_bp, url_prefix='/api/market')

# Live data routes (real-time quotes and intraday data)
from routes.live import live_bp
app.register_blueprint(live_bp, url_prefix='/api/live')

# Admin Vendors
from routes.admin.vendors import vendors_bp
app.register_blueprint(vendors_bp, url_prefix='/api/admin')

# Admin Testimonials
from routes.admin.testimonials import admin_testimonials_bp
app.register_blueprint(admin_testimonials_bp, url_prefix='/api/admin')

# Admin FAQ
from routes.admin.faq import admin_faq_bp
app.register_blueprint(admin_faq_bp, url_prefix='/api/admin')

# Admin API Management
from routes.admin.api_management import admin_api_management_bp
app.register_blueprint(admin_api_management_bp, url_prefix='/api/admin')


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    """
    Global crash catcher. 
    In Production: Returns a polite message instead of raw code errors.
    In Development: Returns the actual error for easy debugging.
    """
    # Log the full error to the server logs so developers can fix it
    app.logger.error(f"Unhandled Exception: {str(e)}", exc_info=True)
    
    # If we are NOT in debug mode (Production), hide the technical details
    if not app.debug:
        return jsonify({
            'error': 'An unexpected error occurred on our server.',
            'message': 'Our team has been notified. Please try again later.',
            'status': 500
        }), 500
        
    # In Debug mode, show the error string for easier development
    return jsonify({'error': str(e)}), 500


def create_app():
    """Application factory for external use (e.g., seed scripts)"""
    return app


# Create tables if they don't exist (for development)
with app.app_context():
    try:
        db.create_all()
        print("[OK] Database tables ready")
        
        # Initialize background job scheduler
        # [PROD FIX] Moved inside __main__ so it starts in production (Gunicorn/UWSGI).
        # This is required for the Sequential Queue and automatic alerts to function.
        enable_scheduler = get_setting_secure('ENABLE_SCHEDULER', 'true').lower() == 'true'
        if enable_scheduler:
            # Logic to prevent double-starting in Flask debug mode (reloader)
            is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
            if not config.DEBUG or is_reloader_process:
                from jobs.scheduler import init_scheduler
                init_scheduler(app)
                status = "(debug mode)" if config.DEBUG else ""
                print(f"[OK] Background scheduler started {status}")
    except Exception as e:
        print(f"[WARNING] Database setup/scheduler note: {e}")


if __name__ == '__main__':
    print(f"[INFO] Starting PeartoFinance API on port {config.PORT}")
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=config.DEBUG  # Only use reloader in debug mode
    )
