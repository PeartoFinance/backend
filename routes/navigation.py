"""
Public Navigation Routes
Serves navigation menu items to frontend
"""
from flask import Blueprint, jsonify, request
from models import NavigationItem

navigation_bp = Blueprint('navigation', __name__, url_prefix='/api')


@navigation_bp.route('/navigation', methods=['GET'])
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
