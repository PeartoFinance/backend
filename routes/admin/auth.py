"""
Admin Authentication Utilities
DEPRECATED: This module is kept for backwards compatibility.
Use the auth_required and admin_required decorators from routes/decorators.py instead.
"""
from ..decorators import admin_required, auth_required

# Re-export for backwards compatibility
__all__ = ['admin_required', 'auth_required']
