"""
Admin Authentication Utilities
Validates X-Admin-Secret or Bearer token for protected admin routes
"""
from flask import request, jsonify
from functools import wraps
import os


def admin_required(f):
    """
    Decorator to require admin authentication.
    Validates X-Admin-Secret header or Bearer token against ADMIN_SECRET_KEY env var.
    In dev mode (localhost), accepts 'dev-admin-secret' as fallback.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header or X-Admin-Secret header
        auth_header = request.headers.get('Authorization', '')
        bearer_token = auth_header[7:] if auth_header.startswith('Bearer ') else ''
        legacy_secret = request.headers.get('X-Admin-Secret', '')
        provided = bearer_token or legacy_secret

        # Get configured secret from environment
        secret = os.environ.get('ADMIN_SECRET_KEY', '')

        # Dev mode: if no secret configured and request is local, accept dev-admin-secret
        if not secret:
            host = request.headers.get('Host', '')
            is_local = (
                host.startswith('localhost') or
                host.startswith('127.0.0.1') or
                ':3000' in host or
                ':3001' in host or
                ':5000' in host
            )
            
            if is_local and provided == 'dev-admin-secret':
                # Dev mode auth successful
                request.is_admin = True
                request.admin_actor = 'admin'
                return f(*args, **kwargs)
            
            # No secret configured
            return jsonify({'error': 'ADMIN_SECRET_KEY not configured'}), 500

        # Validate provided secret
        if not provided or provided != secret:
            return jsonify({'error': 'Unauthorized'}), 401

        # Auth successful
        request.is_admin = True
        request.admin_actor = 'admin'
        return f(*args, **kwargs)

    return decorated
