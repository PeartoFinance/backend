"""
Admin Routes Package
Organized admin API routes for PeartoFinance
"""
from flask import Blueprint
from .dashboard import dashboard_bp
from .users import users_bp
from .news import news_bp
from .tools import tools_bp
from .content import content_bp
from .team import team_bp
from .settings import settings_bp
from .audit import audit_bp

# Main admin blueprint
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Register sub-blueprints
admin_bp.register_blueprint(dashboard_bp)
admin_bp.register_blueprint(users_bp)
admin_bp.register_blueprint(news_bp)
admin_bp.register_blueprint(tools_bp)
admin_bp.register_blueprint(content_bp)
admin_bp.register_blueprint(team_bp)
admin_bp.register_blueprint(settings_bp)
admin_bp.register_blueprint(audit_bp)

__all__ = ['admin_bp']
