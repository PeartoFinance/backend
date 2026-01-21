"""
Social API Routes Package
PeartoFinance Backend
"""
from flask import Blueprint
from .profiles import profiles_bp
from .follows import follows_bp
from .messages import messages_bp
from .ideas import ideas_bp
from .groups import groups_bp
from .badges import badges_bp

social_bp = Blueprint('social', __name__)

# Register sub-blueprints
social_bp.register_blueprint(profiles_bp)
social_bp.register_blueprint(follows_bp)
social_bp.register_blueprint(messages_bp)
social_bp.register_blueprint(ideas_bp)
social_bp.register_blueprint(groups_bp)
social_bp.register_blueprint(badges_bp)

__all__ = ['social_bp']
