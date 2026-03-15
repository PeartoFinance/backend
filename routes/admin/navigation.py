"""
Admin Navigation Management Routes
CRUD for navigation menu items
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ..decorators import admin_required, permission_required
from models import db, NavigationItem

navigation_bp = Blueprint('admin_navigation', __name__)


# Navigation sections
SECTIONS = [
    'sidebar_main',
    'sidebar_media', 
    'sidebar_tools',
    'sidebar_auth',
    'sidebar_community',
    'header_pillars',
    'header_tools',
    'header_resources',
    'header_featured',
    'footer_markets',
    'footer_resources',
    'footer_company',
    'footer_legal',
    'mobile'
]


@navigation_bp.route('/navigation', methods=['GET'])
@permission_required("content")
def get_navigation_items():
    """List all navigation items with optional filtering"""
    try:
        section = request.args.get('section')
        is_active = request.args.get('is_active')
        
        query = NavigationItem.query
        
        if section:
            query = query.filter(NavigationItem.section == section)
        if is_active is not None:
            query = query.filter(NavigationItem.is_active == (is_active.lower() == 'true'))
        
        items = query.order_by(NavigationItem.section, NavigationItem.order_index).all()
        
        return jsonify({
            'items': [item.to_dict() for item in items],
            'sections': SECTIONS
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation', methods=['POST'])
@permission_required("content")
def create_navigation_item():
    """Create a new navigation item"""
    try:
        data = request.get_json()
        
        if not data.get('label'):
            return jsonify({'error': 'Label is required'}), 400
        
        # Get next order index for section
        section = data.get('section', 'sidebar_main')
        max_order = db.session.query(db.func.max(NavigationItem.order_index)).filter(
            NavigationItem.section == section
        ).scalar() or 0
        
        item = NavigationItem(
            label=data.get('label'),
            url=data.get('url', ''),
            icon=data.get('icon', ''),
            parent_id=data.get('parent_id'),
            section=section,
            link_type=data.get('link_type', 'internal'),
            badge_text=data.get('badge_text'),
            css_class=data.get('css_class'),
            order_index=max_order + 1,
            is_active=data.get('is_active', True),
            requires_auth=data.get('requires_auth', False),
            roles_allowed=data.get('roles_allowed'),
            country_code=data.get('country_code'),
            created_at=datetime.utcnow()
        )
        
        db.session.add(item)
        db.session.commit()
        
        return jsonify({'ok': True, 'item': item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/<int:item_id>', methods=['GET'])
@permission_required("content")
def get_navigation_item(item_id):
    """Get a single navigation item"""
    try:
        item = NavigationItem.query.get_or_404(item_id)
        return jsonify({'item': item.to_dict()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/<int:item_id>', methods=['PUT'])
@permission_required("content")
def update_navigation_item(item_id):
    """Update a navigation item"""
    try:
        item = NavigationItem.query.get_or_404(item_id)
        data = request.get_json()
        
        # Update fields
        updateable_fields = [
            'label', 'url', 'icon', 'parent_id', 'section', 'link_type',
            'badge_text', 'css_class', 'order_index', 'is_active',
            'requires_auth', 'roles_allowed', 'country_code'
        ]
        
        for field in updateable_fields:
            if field in data:
                setattr(item, field, data[field])
        
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'ok': True, 'item': item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/<int:item_id>', methods=['DELETE'])
@permission_required("content")
def delete_navigation_item(item_id):
    """Delete a navigation item"""
    try:
        item = NavigationItem.query.get_or_404(item_id)
        
        # Also delete children
        NavigationItem.query.filter_by(parent_id=item_id).delete()
        
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/<int:item_id>/toggle', methods=['PUT'])
@permission_required("content")
def toggle_navigation_item(item_id):
    """Toggle active status of a navigation item"""
    try:
        item = NavigationItem.query.get_or_404(item_id)
        item.is_active = not item.is_active
        item.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'ok': True, 'is_active': item.is_active})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/reorder', methods=['PUT'])
@permission_required("content")
def reorder_navigation_items():
    """Bulk reorder navigation items"""
    try:
        data = request.get_json()
        items = data.get('items', [])
        
        for idx, item_data in enumerate(items):
            item = NavigationItem.query.get(item_data.get('id'))
            if item:
                item.order_index = idx
                if 'section' in item_data:
                    item.section = item_data['section']
        
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@navigation_bp.route('/navigation/seed', methods=['POST'])
@permission_required("content")
def seed_navigation():
    """Seed default navigation items based on current hardcoded structure"""
    try:
        # Check if already seeded
        if NavigationItem.query.count() > 0:
            return jsonify({'message': 'Navigation already has items', 'count': NavigationItem.query.count()})
        
        default_items = [
            # Sidebar Main
            {'label': 'Dashboard', 'url': '/', 'icon': 'LayoutDashboard', 'section': 'sidebar_main', 'order_index': 1},
            {'label': 'Markets', 'url': '/markets', 'icon': 'TrendingUp', 'section': 'sidebar_main', 'order_index': 2},
            {'label': 'News', 'url': '/news', 'icon': 'Newspaper', 'section': 'sidebar_main', 'order_index': 3},
            {'label': 'Learn', 'url': '/learn', 'icon': 'GraduationCap', 'section': 'sidebar_main', 'order_index': 4},
            
            # Sidebar Auth (requires login)
            {'label': 'Portfolio', 'url': '/portfolio', 'icon': 'Briefcase', 'section': 'sidebar_auth', 'order_index': 1, 'requires_auth': True},
            {'label': 'My Watchlist', 'url': '/watchlist', 'icon': 'Star', 'section': 'sidebar_auth', 'order_index': 2, 'requires_auth': True},
            {'label': 'My Courses', 'url': '/my-courses', 'icon': 'BookOpen', 'section': 'sidebar_auth', 'order_index': 3, 'requires_auth': True},
            
            # Sidebar Media
            {'label': 'Live TV', 'url': '/tv', 'icon': 'Tv', 'section': 'sidebar_media', 'order_index': 1},
            {'label': 'Radio', 'url': '/radio', 'icon': 'Radio', 'section': 'sidebar_media', 'order_index': 2},
            {'label': 'Live Sports', 'url': '/sports', 'icon': 'Zap', 'section': 'sidebar_media', 'order_index': 3},
            
            # Sidebar Tools
            {'label': 'SIP Calculator', 'url': '/tools/sip', 'icon': 'Calculator', 'section': 'sidebar_tools', 'order_index': 1},
            {'label': 'EMI Calculator', 'url': '/tools/emi', 'icon': 'Calculator', 'section': 'sidebar_tools', 'order_index': 2},
            {'label': 'Compound Interest', 'url': '/tools/compound', 'icon': 'Calculator', 'section': 'sidebar_tools', 'order_index': 3},
            
            # Header Pillars
            {'label': 'Stocks', 'url': '/stocks', 'icon': 'TrendingUp', 'section': 'header_pillars', 'order_index': 1},
            {'label': 'Crypto', 'url': '/crypto', 'icon': 'Bitcoin', 'section': 'header_pillars', 'order_index': 2},
            {'label': 'Forex', 'url': '/forex', 'icon': 'DollarSign', 'section': 'header_pillars', 'order_index': 3},
            {'label': 'Commodities', 'url': '/commodities', 'icon': 'BarChart3', 'section': 'header_pillars', 'order_index': 4},
            
            # Header Featured
            {'label': 'Markets', 'url': '/markets', 'icon': 'TrendingUp', 'section': 'header_featured', 'order_index': 1, 'css_class': 'bg-gradient-to-br from-blue-600 via-indigo-600 to-purple-600'},
            {'label': 'Booyah', 'url': '/booyah', 'icon': 'Sparkles', 'section': 'header_featured', 'order_index': 2, 'css_class': 'bg-gradient-to-br from-green-500 via-emerald-500 to-green-600'},
            
            # Header Tools
            {'label': 'SIP Calculator', 'url': '/tools/sip', 'icon': 'Calculator', 'section': 'header_tools', 'order_index': 1},
            {'label': 'EMI Calculator', 'url': '/tools/emi', 'icon': 'Calculator', 'section': 'header_tools', 'order_index': 2},
            {'label': 'Compound Interest', 'url': '/tools/compound', 'icon': 'PiggyBank', 'section': 'header_tools', 'order_index': 3},
            {'label': 'Retirement Planner', 'url': '/tools/retirement', 'icon': 'Landmark', 'section': 'header_tools', 'order_index': 4},
            
            # Header Resources
            {'label': 'Learn', 'url': '/learn', 'icon': 'GraduationCap', 'section': 'header_resources', 'order_index': 1},
            {'label': 'News', 'url': '/news', 'icon': 'Newspaper', 'section': 'header_resources', 'order_index': 2},
            {'label': 'Live TV', 'url': '/tv', 'icon': 'Tv', 'section': 'header_resources', 'order_index': 3},
            {'label': 'Radio', 'url': '/radio', 'icon': 'Radio', 'section': 'header_resources', 'order_index': 4},
            {'label': 'Blog', 'url': '/blog', 'icon': 'FileText', 'section': 'header_resources', 'order_index': 5},
            {'label': 'Help Center', 'url': '/help', 'icon': 'HelpCircle', 'section': 'header_resources', 'order_index': 6},
            
            # Sidebar Community
            {'label': 'Trading Ideas', 'url': '/ideas', 'icon': 'Lightbulb', 'section': 'sidebar_community', 'order_index': 1},
            {'label': 'Discussion Groups', 'url': '/groups', 'icon': 'Users', 'section': 'sidebar_community', 'order_index': 2},
            {'label': 'Discover Investors', 'url': '/investors', 'icon': 'User', 'section': 'sidebar_community', 'order_index': 3},
            {'label': 'Badges', 'url': '/badges', 'icon': 'Award', 'section': 'sidebar_community', 'order_index': 4},
            {'label': 'Messages', 'url': '/messages', 'icon': 'MessageCircle', 'section': 'sidebar_community', 'order_index': 5, 'requires_auth': True},
            
            # Footer Markets
            {'label': 'Stocks', 'url': '/stocks', 'icon': '', 'section': 'footer_markets', 'order_index': 1},
            {'label': 'Cryptocurrency', 'url': '/crypto', 'icon': '', 'section': 'footer_markets', 'order_index': 2},
            {'label': 'Forex', 'url': '/forex', 'icon': '', 'section': 'footer_markets', 'order_index': 3},
            {'label': 'Market Overview', 'url': '/markets', 'icon': '', 'section': 'footer_markets', 'order_index': 4},
            
            # Footer Resources
            {'label': 'Financial Tools', 'url': '/tools', 'icon': '', 'section': 'footer_resources', 'order_index': 1},
            {'label': 'Learn Investing', 'url': '/learn', 'icon': '', 'section': 'footer_resources', 'order_index': 2},
            {'label': 'Market News', 'url': '/news', 'icon': '', 'section': 'footer_resources', 'order_index': 3},
            {'label': 'Glossary', 'url': '/glossary', 'icon': '', 'section': 'footer_resources', 'order_index': 4},
            
            # Footer Company
            {'label': 'About Us', 'url': '/p/about', 'icon': '', 'section': 'footer_company', 'order_index': 1},
            {'label': 'Contact', 'url': '/p/contact', 'icon': '', 'section': 'footer_company', 'order_index': 2},
            {'label': 'Careers', 'url': '/p/careers', 'icon': '', 'section': 'footer_company', 'order_index': 3},
            {'label': 'Press', 'url': '/p/press', 'icon': '', 'section': 'footer_company', 'order_index': 4},
            
            # Footer Legal
            {'label': 'Privacy Policy', 'url': '/p/privacy', 'icon': '', 'section': 'footer_legal', 'order_index': 1},
            {'label': 'Terms of Service', 'url': '/p/terms', 'icon': '', 'section': 'footer_legal', 'order_index': 2},
            {'label': 'Disclaimer', 'url': '/p/disclaimer', 'icon': '', 'section': 'footer_legal', 'order_index': 3},
            {'label': 'Cookie Policy', 'url': '/p/cookies', 'icon': '', 'section': 'footer_legal', 'order_index': 4},
        ]
        
        for item_data in default_items:
            item = NavigationItem(**item_data)
            db.session.add(item)
        
        db.session.commit()
        
        return jsonify({'ok': True, 'message': f'Seeded {len(default_items)} navigation items'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
