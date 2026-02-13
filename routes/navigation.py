"""
Public Navigation Routes
Serves navigation menu items to frontend
"""
from flask import Blueprint, jsonify, request
from models import NavigationItem, Settings
from extensions import cache

navigation_bp = Blueprint('navigation', __name__)


@navigation_bp.route('/navigation', methods=['GET'])
@cache.cached(timeout=300, query_string=True)
def get_public_navigation():
    """Get all active navigation items for public use"""
    try:
        section = request.args.get('section')
        country = getattr(request, 'user_country', None)
        
        query = NavigationItem.query.filter(NavigationItem.is_active == True)
        
        if section:
            query = query.filter(NavigationItem.section == section)
        
        # Filter by country if specified
        if country:
            query = query.filter(
                (NavigationItem.country_code == country) | 
                (NavigationItem.country_code == None)
            )
        
        items = query.order_by(NavigationItem.section, NavigationItem.order_index).all()
        
        # Group by section
        grouped = {}
        for item in items:
            section_name = item.section or 'default'
            if section_name not in grouped:
                grouped[section_name] = []
            grouped[section_name].append(item.to_dict())
        
        return jsonify({
            'navigation': grouped,
            'items': [item.to_dict() for item in items]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/feature-flags', methods=['GET'])
@cache.cached(timeout=120, query_string=True)
def get_public_feature_flags():
    """
    Get public feature flags for frontend.
    Used to control AI widgets visibility, maintenance mode, etc.
    No authentication required.
    """
    try:
        # Default feature flags
        flags = {
            'ai_widgets_enabled': True,      # Show AI widgets on pages
            'ai_analysis_enabled': True,     # Show AI analysis panels
            'maintenance_mode': False,       # Site maintenance mode
        }
        
        # Load actual values from settings table
        settings = Settings.query.filter(
            Settings.category == 'feature_flags',
            Settings.is_public == True
        ).all()
        
        for s in settings:
            if s.type == 'boolean':
                flags[s.key] = s.value == 'true'
            else:
                flags[s.key] = s.value
        
        return jsonify(flags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

