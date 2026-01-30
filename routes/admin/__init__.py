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
from .marketing import marketing_bp
from .tasks import tasks_bp
from .support import support_bp
from .jobs import jobs_bp
from .market import market_bp
from .media import media_bp
from .education import education_admin_bp
from .roles import roles_bp
from .uploads import uploads_bp
from .email_templates import email_templates_bp
from .navigation import navigation_bp
from .financial import financial_bp
from .products import products_bp
from .orders import orders_bp
from .pricing import pricing_bp
from .sellers import sellers_bp
from .help import help_bp
from .ai import ai_bp
from .bookings import bookings_bp

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
admin_bp.register_blueprint(marketing_bp)
admin_bp.register_blueprint(tasks_bp)
admin_bp.register_blueprint(support_bp)
admin_bp.register_blueprint(jobs_bp)
admin_bp.register_blueprint(market_bp)
admin_bp.register_blueprint(media_bp)
admin_bp.register_blueprint(education_admin_bp)
admin_bp.register_blueprint(roles_bp)
admin_bp.register_blueprint(uploads_bp)
admin_bp.register_blueprint(email_templates_bp)
admin_bp.register_blueprint(navigation_bp)
admin_bp.register_blueprint(financial_bp)
admin_bp.register_blueprint(products_bp)
admin_bp.register_blueprint(orders_bp)
admin_bp.register_blueprint(pricing_bp)
admin_bp.register_blueprint(sellers_bp)
admin_bp.register_blueprint(help_bp)
admin_bp.register_blueprint(ai_bp)
admin_bp.register_blueprint(bookings_bp)

__all__ = ['admin_bp']
