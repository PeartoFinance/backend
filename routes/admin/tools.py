"""
Admin Tools Management Routes
CRUD for /api/admin/tools
"""
from flask import Blueprint, jsonify, request
from functools import wraps
from models import db, ToolSettings

tools_bp = Blueprint('admin_tools', __name__)


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        admin_secret = request.headers.get('X-Admin-Secret')
        if not admin_secret:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated


@tools_bp.route('/tools', methods=['GET'])
@admin_required
def get_tools():
    """List all tool settings"""
    try:
        tools = ToolSettings.query.order_by(ToolSettings.order_index).all()
        return jsonify({
            'tools': [{
                'id': t.id,
                'tool_slug': t.tool_slug,
                'enabled': t.enabled,
                'is_implemented': t.is_implemented,
                'order_index': t.order_index,
                'category': t.category,
            } for t in tools]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tools_bp.route('/tools/<int:tool_id>', methods=['PATCH'])
@admin_required
def update_tool(tool_id):
    """Update tool settings"""
    try:
        tool = ToolSettings.query.get_or_404(tool_id)
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
        
        ToolSettings.query.filter(ToolSettings.id.in_(tool_ids)).update(
            {'enabled': enabled}, synchronize_session=False
        )
        db.session.commit()
        return jsonify({'ok': True, 'updated': len(tool_ids)})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
