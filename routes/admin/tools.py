"""
Admin Tools Management Routes
CRUD for /api/admin/tools
"""
from flask import Blueprint, jsonify, request
from .auth import admin_required
from models import db, ToolSettings

tools_bp = Blueprint('admin_tools', __name__)


@tools_bp.route('/tools', methods=['GET'])
@admin_required
def get_tools():
    """List all tool settings"""
    try:
        tools = ToolSettings.query.order_by(ToolSettings.order_index).all()
        return jsonify({
            'tools': [{
                'tool_slug': t.tool_slug,
                'tool_name': t.tool_name,
                'enabled': t.enabled,
                'is_implemented': t.is_implemented,
                'order_index': t.order_index,
                'category': t.category or 'General',
                'country_code': t.country_code,
            } for t in tools]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools/<tool_slug>', methods=['PATCH', 'PUT'])
@admin_required
def update_tool(tool_slug):
    """Update tool settings by slug"""
    try:
        tool = ToolSettings.query.get_or_404(tool_slug)
        data = request.get_json()
        
        if 'enabled' in data:
            tool.enabled = data['enabled']
        if 'is_implemented' in data:
            tool.is_implemented = data['is_implemented']
        if 'order_index' in data:
            tool.order_index = data['order_index']
        if 'category' in data:
            tool.category = data['category']
        
        db.session.commit()
        return jsonify({'ok': True, 'tool_slug': tool_slug, 'enabled': tool.enabled})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools/bulk', methods=['PUT', 'POST'])
@admin_required
def bulk_toggle_tools():
    """Enable/disable multiple tools by slugs"""
    try:
        data = request.get_json()
        slugs = data.get('slugs', [])
        enabled = data.get('enabled', True)
        
        if not slugs:
            return jsonify({'error': 'No slugs provided'}), 400
        
        ToolSettings.query.filter(ToolSettings.tool_slug.in_(slugs)).update(
            {'enabled': enabled}, synchronize_session=False
        )
        db.session.commit()
        return jsonify({'ok': True, 'updated': len(slugs)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
