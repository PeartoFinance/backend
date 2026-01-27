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
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
from models.base import db
from flask_migrate import Migrate

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS

# Initialize SQLAlchemy
db.init_app(app)

# For migration
migrate = Migrate(app, db)

# Import all models so Alembic can detect them during migration
import models


# Configure CORS - explicitly list all allowed origins (cannot use * with credentials)
CORS(app, 
     origins=[
         "http://localhost:3000",
         "http://localhost:3001",
         "http://127.0.0.1:3000",
         "http://192.168.1.71:3000",
         "http://192.168.1.71:3001",
         "http://192.168.1.71:5000",
         "https://pearto.com",
         "https://www.pearto.com",
         "https://test.pearto.com",
         "http://192.168.1.71:5000",
         "https://frontend-admin-pearto.vercel.app",
         "https://stocks-nine-blush.vercel.app",
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

# User feature routes
from routes.alerts import alerts_bp
from routes.documents import documents_bp
app.register_blueprint(alerts_bp, url_prefix='/api/user/alerts')
app.register_blueprint(documents_bp, url_prefix='/api/user/documents')
app.register_blueprint(news_prefs_bp, url_prefix='/api/user/news-preferences')

# Cron routes for external cURL calls (cPanel)
from routes.cron import cron_bp
app.register_blueprint(cron_bp, url_prefix='/api/cron')

# Market status routes (market hours, open/close status)
from routes.market_status import market_status_bp
app.register_blueprint(market_status_bp, url_prefix='/api/market')


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


@app.errorhandler(Exception)
def handle_exception(e):
    return jsonify({'error': str(e)}), 500


def create_app():
    """Application factory for external use (e.g., seed scripts)"""
    return app


# Create tables if they don't exist (for development)
with app.app_context():
    try:
        db.create_all()
        print("[OK] Database tables ready")
    except Exception as e:
        print(f"[WARNING] Database setup note: {e}")


if __name__ == '__main__':
    import os
    
    # Initialize background job scheduler
    # Only run scheduler in the main process, not in the reloader child process
    # When Flask debug mode is on, WERKZEUG_RUN_MAIN is set to 'true' in the child process
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    enable_scheduler = os.getenv('ENABLE_SCHEDULER', 'true').lower() == 'true'
    
    # In debug mode, only start scheduler in the reloader child process (after restart)
    # In production (non-debug), start scheduler immediately
    if enable_scheduler:
        if config.DEBUG:
            if is_reloader_process:
                from jobs.scheduler import init_scheduler
                init_scheduler(app)
                print("[OK] Background scheduler started (debug mode)")
        else:
            from jobs.scheduler import init_scheduler
            init_scheduler(app)
            print("[OK] Background scheduler started")
    
    print(f"[INFO] Starting PeartoFinance API on port {config.PORT}")
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG,
        use_reloader=config.DEBUG  # Only use reloader in debug mode
    )
