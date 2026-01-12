"""
Tools API Routes
Handles tool settings and calculator management
"""
from flask import Blueprint, request, jsonify
from models.settings import ToolSettings
from models.base import db

tools_bp = Blueprint('tools', __name__, url_prefix='/api/tools')


def get_country_context():
    """Get country from request headers with fallback"""
    admin_header = request.headers.get('X-Admin-Country')
    user_header = request.headers.get('X-User-Country')
    
    # Admin header takes precedence
    if admin_header:
        if admin_header.upper() == 'GLOBAL':
            return {'is_global': True, 'country_code': 'US'}
        return {'is_global': False, 'country_code': admin_header.upper()}
    
    # User header from frontend
    if user_header:
        return {'is_global': False, 'country_code': user_header.upper()}
    
    # Default fallback
    return {'is_global': True, 'country_code': 'US'}


def deduplicate_tools(tools, user_country):
    """Deduplicate tools by priority: UserCountry > GLOBAL > US"""
    tool_map = {}
    
    def get_priority(code):
        if code == user_country:
            return 3
        if code == 'GLOBAL':
            return 2
        if code == 'US':
            return 1
        return 0
    
    for tool in tools:
        slug = tool.tool_slug
        cc = (tool.country_code or 'US').upper()
        priority = get_priority(cc)
        
        if slug not in tool_map or priority > tool_map[slug]['priority']:
            tool_map[slug] = {
                'tool': tool,
                'priority': priority
            }
    
    # Sort by category then order_index
    result = [item['tool'] for item in tool_map.values()]
    result.sort(key=lambda t: (t.category or '', t.order_index or 0))
    return result


@tools_bp.route('/settings', methods=['GET'])
def get_tools_settings():
    """List all tool settings (admin view, country-filtered)"""
    ctx = get_country_context()
    
    query = ToolSettings.query
    
    if not ctx['is_global'] and ctx['country_code']:
        # Filter by user country or GLOBAL
        query = query.filter(
            db.or_(
                ToolSettings.country_code == ctx['country_code'],
                ToolSettings.country_code == 'GLOBAL'
            )
        )
    else:
        # Show GLOBAL and US
        query = query.filter(
            db.or_(
                ToolSettings.country_code == 'GLOBAL',
                ToolSettings.country_code == 'US'
            )
        )
    
    tools = query.all()
    unique_tools = deduplicate_tools(tools, ctx['country_code'])
    
    return jsonify([t.to_dict() for t in unique_tools])


@tools_bp.route('/settings/enabled', methods=['GET'])
def get_enabled_tools():
    """List only enabled tools (public, country-filtered)"""
    ctx = get_country_context()
    
    query = ToolSettings.query.filter(ToolSettings.enabled == True)
    
    if not ctx['is_global'] and ctx['country_code']:
        query = query.filter(
            db.or_(
                ToolSettings.country_code == ctx['country_code'],
                ToolSettings.country_code == 'GLOBAL'
            )
        )
    else:
        query = query.filter(
            db.or_(
                ToolSettings.country_code == 'GLOBAL',
                ToolSettings.country_code == 'US'
            )
        )
    
    tools = query.all()
    unique_tools = deduplicate_tools(tools, ctx['country_code'])
    
    return jsonify([t.to_dict() for t in unique_tools])

