"""
Admin Tools Management Routes
CRUD for /api/admin/tools
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from models import db, ToolSettings
from ..decorators import admin_required


tools_bp = Blueprint('admin_tools', __name__)

    
@tools_bp.route('/tools', methods=['GET'])
@admin_required
def get_tools():
    """List all tool settings"""
    try:
        # Filter by user's country or GLOBAL settings
        country = getattr(request, 'user_country', 'US')
        is_global = not country or country == 'GLOBAL'
        
        query = ToolSettings.query
        if not is_global:
            query = query.filter(
                (ToolSettings.country_code == country) | 
                (ToolSettings.country_code == 'GLOBAL')
            )
        tools = query.order_by(ToolSettings.order_index).all()
        
        return jsonify({
            'tools': [{
                'id': t.tool_slug, # Use slug as ID
                'tool_slug': t.tool_slug,
                'tool_name': t.tool_name,
                'enabled': t.enabled,
                'is_implemented': t.is_implemented,
                'order_index': t.order_index,
                'category': t.category,
                'country_code': t.country_code
            } for t in tools]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools', methods=['POST'])
@admin_required
def create_tool():
    """Create new tool setting"""
    try:
        data = request.get_json()
        
        # Validation
        if not data.get('tool_slug'):
            return jsonify({'error': 'tool_slug is required'}), 400
            
        # Check if exists
        if ToolSettings.query.filter_by(tool_slug=data['tool_slug']).first():
            return jsonify({'error': 'Tool with this slug already exists'}), 400
            
        tool = ToolSettings(
            tool_slug=data['tool_slug'],
            tool_name=data.get('tool_name', data['tool_slug'].replace('-', ' ').title()), # Default name from slug
            enabled=data.get('enabled', True),
            is_implemented=data.get('is_implemented', False),
            order_index=data.get('order_index', 0),
            category=data.get('category', 'general'),
            country_code=data.get('country_code', getattr(request, 'user_country', 'GLOBAL'))
        )
        
        db.session.add(tool)
        db.session.commit()
        
        return jsonify({
            'ok': True, 
            'id': tool.tool_slug, # Use slug as ID
            'message': 'Tool created successfully'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools/<string:tool_slug>', methods=['PATCH'])
@admin_required
def update_tool(tool_slug):
    """Update tool settings"""
    try:
        tool = ToolSettings.query.get_or_404(tool_slug)
        data = request.get_json()
        
        if 'enabled' in data:
            tool.enabled = data['enabled']
        if 'tool_name' in data:
            tool.tool_name = data['tool_name']
        if 'is_implemented' in data:
            tool.is_implemented = data['is_implemented']
        if 'order_index' in data:
            tool.order_index = data['order_index']
        if 'category' in data:
            tool.category = data['category']
        if 'country_code' in data:
            tool.country_code = data['country_code']
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools/bulk-toggle', methods=['POST'])
@admin_required
def bulk_toggle_tools():
    """Enable/disable multiple tools"""
    try:
        data = request.get_json()
        tool_ids = data.get('tool_ids', [])
        enabled = data.get('enabled', True)
        
        ToolSettings.query.filter(ToolSettings.tool_slug.in_(tool_ids)).update(
            {'enabled': enabled}, synchronize_session=False
        )
        db.session.commit()
        return jsonify({'ok': True, 'updated': len(tool_ids)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
