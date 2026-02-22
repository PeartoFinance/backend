"""
Admin Roles Management Routes
RBAC system for admin panel access control
"""
from flask import Blueprint, jsonify, request, g
from ..decorators import auth_required
from models import db, Role, AdminUser, User
from datetime import datetime

roles_bp = Blueprint('admin_roles', __name__)


def superadmin_required(f):
    """Decorator to require superadmin access"""
    from functools import wraps
    @wraps(f)
    @auth_required
    def decorated(*args, **kwargs):
        user = getattr(request, 'user', None)
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        
        # Check if user is superadmin
        admin_user = AdminUser.query.filter_by(user_id=user.id).first()
        if not admin_user or not admin_user.is_superadmin:
            return jsonify({'error': 'Superadmin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated


def admin_with_permission(permission_key):
    """Decorator factory to require specific permission"""
    from functools import wraps
    def decorator(f):
        @wraps(f)
        @auth_required
        def decorated(*args, **kwargs):
            user = getattr(request, 'user', None)
            if not user:
                return jsonify({'error': 'Authentication required'}), 401
            
            admin_user = AdminUser.query.filter_by(user_id=user.id).first()
            if not admin_user:
                return jsonify({'error': 'Admin access required'}), 403
            
            permissions = admin_user.get_permissions()
            if not permissions.get(permission_key, False):
                return jsonify({'error': f'Permission "{permission_key}" required'}), 403
            
            return f(*args, **kwargs)
        return decorated
    return decorator


# ============================================================================
# PERMISSION KEYS
# ============================================================================

@roles_bp.route('/permission-keys', methods=['GET'])
@superadmin_required
def get_permission_keys():
    """Get all available permission keys"""
    return jsonify({
        'keys': Role.PERMISSION_KEYS,
        'descriptions': {
            'dashboard': 'Dashboard overview',
            'content': 'Content management (posts, pages, navigation)',
            'educational': 'Courses and instructors',
            'news_media': 'News, radio, TV, RSS feeds',
            'live_sports': 'Manage live sports events',
            'sports_config': 'Configure sports API and settings',
            'events_jobs': 'Events and job listings',
            'help_center': 'Help categories and articles',
            'users_access': 'User management and roles',
            'users_view': 'View and edit user profiles',
            'roles_management': 'Manage and assign admin roles',
            'subscriptions_view': 'Manage user subscriptions',
            'bookings': 'Booking management',
            'business': 'Products, orders, vendors',
            'vendors_manage': 'Manage vendor profiles',
            'sellers_manage': 'Manage seller profiles',
            'seller_applications': 'Review seller applications',
            'financial': 'Transactions, deposits, withdrawals',
            'transactions_view': 'View financial transactions',
            'deposits_manage': 'Approve/Reject deposits',
            'withdrawals_manage': 'Approve/Reject withdrawals',
            'market_data': 'Stocks, crypto, indices, commodities',
            'business_profiles': 'Business directory and profiles',
            'marketing': 'Campaigns, subscribers, affiliates',
            'communications': 'Messages, comments, emails',
            'ai_features': 'AI features access',
            'ai_agent': 'Access to AI trading agent',
            'ai_content_writer': 'Access to AI content writer',
            'system': 'System management',
            'system_tools': 'Access to diagnostic tools',
            'system_tasks': 'Manage admin tasks',
            'system_scheduler': 'Manage cron jobs and scheduler',
            'system_audit': 'View system audit logs',
            'apis_integration': 'API control and registry',
            'configuration': 'Settings and appearance',
        }
    })


# ============================================================================
# ROLES CRUD
# ============================================================================

@roles_bp.route('/roles', methods=['GET'])
@superadmin_required
def get_roles():
    """Get all roles"""
    roles = Role.query.order_by(Role.name).all()
    return jsonify({
        'roles': [r.to_dict() for r in roles]
    })


@roles_bp.route('/roles/<int:role_id>', methods=['GET'])
@superadmin_required
def get_role(role_id):
    """Get single role"""
    role = Role.query.get_or_404(role_id)
    return jsonify(role.to_dict())


@roles_bp.route('/roles', methods=['POST'])
@superadmin_required
def create_role():
    """Create a new role"""
    data = request.get_json()
    
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Role name is required'}), 400
    
    # Check if name exists
    if Role.query.filter_by(name=name).first():
        return jsonify({'error': 'Role name already exists'}), 400
    
    role = Role(
        name=name,
        description=data.get('description', ''),
        permissions=data.get('permissions', Role.get_default_admin_permissions()),
        is_system=False,
        created_by=request.user.id
    )
    
    db.session.add(role)
    db.session.commit()
    
    return jsonify(role.to_dict()), 201


@roles_bp.route('/roles/<int:role_id>', methods=['PUT'])
@superadmin_required
def update_role(role_id):
    """Update a role"""
    role = Role.query.get_or_404(role_id)
    
    if role.is_system:
        return jsonify({'error': 'System roles cannot be modified'}), 400
    
    data = request.get_json()
    
    if 'name' in data:
        name = data['name'].strip()
        existing = Role.query.filter(Role.name == name, Role.id != role_id).first()
        if existing:
            return jsonify({'error': 'Role name already exists'}), 400
        role.name = name
    
    if 'description' in data:
        role.description = data['description']
    
    if 'permissions' in data:
        role.permissions = data['permissions']
    
    db.session.commit()
    return jsonify(role.to_dict())


@roles_bp.route('/roles/<int:role_id>', methods=['DELETE'])
@superadmin_required
def delete_role(role_id):
    """Delete a role"""
    role = Role.query.get_or_404(role_id)
    
    if role.is_system:
        return jsonify({'error': 'System roles cannot be deleted'}), 400
    
    # Check if role is assigned to any admins
    if AdminUser.query.filter_by(role_id=role_id).count() > 0:
        return jsonify({'error': 'Cannot delete role assigned to admins. Reassign them first.'}), 400
    
    db.session.delete(role)
    db.session.commit()
    return jsonify({'message': 'Role deleted'})


# ============================================================================
# ADMIN USERS
# ============================================================================

@roles_bp.route('/users/search', methods=['GET'])
@superadmin_required
def search_users():
    """Search users to assign as admins"""
    query = request.args.get('q', '').strip()
    if len(query) < 2:
        return jsonify({'users': []})
    
    # Search by name or email
    users = User.query.filter(
        (User.name.ilike(f'%{query}%')) | (User.email.ilike(f'%{query}%'))
    ).limit(20).all()
    
    # Exclude users who are already admins
    admin_user_ids = {a.user_id for a in AdminUser.query.all()}
    
    return jsonify({
        'users': [{
            'id': u.id,
            'name': u.name,
            'email': u.email,
            'avatarUrl': u.avatar_url,
            'role': u.role,
            'isAdmin': u.id in admin_user_ids
        } for u in users]
    })


@roles_bp.route('/admins', methods=['GET'])
@superadmin_required
def get_admins():
    """Get all admin users"""
    admins = AdminUser.query.all()
    return jsonify({
        'admins': [a.to_dict() for a in admins]
    })


@roles_bp.route('/admins', methods=['POST'])
@superadmin_required
def create_admin():
    """Assign admin role to a user"""
    data = request.get_json()
    
    user_id = data.get('userId')
    role_id = data.get('roleId')
    is_superadmin = data.get('isSuperadmin', False)
    
    if not user_id or not role_id:
        return jsonify({'error': 'userId and roleId are required'}), 400
    
    # Check user exists
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Check role exists
    role = Role.query.get(role_id)
    if not role:
        return jsonify({'error': 'Role not found'}), 404
    
    # Check not already admin
    if AdminUser.query.filter_by(user_id=user_id).first():
        return jsonify({'error': 'User is already an admin'}), 400
    
    admin_user = AdminUser(
        user_id=user_id,
        role_id=role_id,
        is_superadmin=is_superadmin,
        created_by=request.user.id
    )
    
    # Also update user.role field
    user.role = 'admin'
    
    db.session.add(admin_user)
    db.session.commit()
    
    return jsonify(admin_user.to_dict()), 201


@roles_bp.route('/admins/<int:admin_id>', methods=['PUT'])
@superadmin_required
def update_admin(admin_id):
    """Update admin's role"""
    admin_user = AdminUser.query.get_or_404(admin_id)
    data = request.get_json()
    
    if 'roleId' in data:
        role = Role.query.get(data['roleId'])
        if not role:
            return jsonify({'error': 'Role not found'}), 404
        admin_user.role_id = data['roleId']
    
    if 'isSuperadmin' in data:
        admin_user.is_superadmin = data['isSuperadmin']
    
    db.session.commit()
    return jsonify(admin_user.to_dict())


@roles_bp.route('/admins/<int:admin_id>', methods=['DELETE'])
@superadmin_required
def remove_admin(admin_id):
    """Remove admin access from user"""
    admin_user = AdminUser.query.get_or_404(admin_id)
    
    # Update user.role back to 'user'
    user = User.query.get(admin_user.user_id)
    if user:
        user.role = 'user'
    
    db.session.delete(admin_user)
    db.session.commit()
    return jsonify({'message': 'Admin access removed'})


# ============================================================================
# CURRENT ADMIN PERMISSIONS
# ============================================================================

@roles_bp.route('/me/permissions', methods=['GET'])
@auth_required
def get_my_permissions():
    """Get current user's admin permissions"""
    user = request.user
    admin_user = AdminUser.query.filter_by(user_id=user.id).first()
    
    if not admin_user:
        return jsonify({'error': 'Not an admin'}), 403
    
    return jsonify({
        'isSuperadmin': admin_user.is_superadmin,
        'role': admin_user.role.to_dict() if admin_user.role else None,
        'permissions': admin_user.get_permissions()
    })
