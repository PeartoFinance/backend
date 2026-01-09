"""
Flask Backend - Main Application
PeartoFinance API Server with SQLAlchemy
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from config import config
from models.base import db

# Initialize Flask app
app = Flask(__name__)

# Load configuration
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = config.SQLALCHEMY_ENGINE_OPTIONS

# Initialize SQLAlchemy
db.init_app(app)

# Configure CORS - allow all origins with explicit headers
CORS(app, 
     origins="*",
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "X-Admin-Secret", "X-Admin-Country", "X-User-Country"],
     methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
     expose_headers=["Content-Type", "Authorization"])


# Middleware to extract country from headers
@app.before_request
def extract_country():
    """Extract user country from X-User-Country header"""
    request.user_country = request.headers.get('X-User-Country', 'US')


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
    print(f"[INFO] Starting PeartoFinance API on port {config.PORT}")
    app.run(
        host='0.0.0.0',
        port=config.PORT,
        debug=config.DEBUG
    )
