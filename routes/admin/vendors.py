"""
Admin Vendor Management Routes
CRUD for Vendors, API Keys, and Webhooks
"""
import uuid
import secrets
import bcrypt
import json
from datetime import datetime, timezone
from flask import Blueprint, jsonify, request
from models import db, Vendor, VendorAPIKey, VendorCustomAPI, AuditEvent
from ..decorators import admin_required

vendors_bp = Blueprint('admin_vendors', __name__)

def log_audit(action, entity, entity_id, meta=None):
    try:
        audit = AuditEvent(
            id=str(uuid.uuid4()),
            actor='admin', # TODO: Get actual admin ID from token/session if available
            action=action,
            entity=entity,
            entityId=entity_id,
            meta=json.dumps(meta) if meta else None
        )
        db.session.add(audit)
    except Exception as e:
        print(f"Audit log failed: {e}")

# ==========================================
# Vendor CRUD
# ==========================================

@vendors_bp.route('/vendors', methods=['GET'])
@admin_required
def get_vendors():
    """List all vendors"""
    try:
        vendors = Vendor.query.order_by(Vendor.created_at.desc()).all()
        # Enrich with key count if possible, or just raw
        results = []
        for v in vendors:
            v_dict = {
                'id': v.id,
                'name': v.name,
                'email': v.email,
                'status': v.status,
                'countryCode': v.country_code,
                'createdAt': v.created_at.isoformat() if v.created_at else None,
                'logoUrl': v.logo_url
            }
            results.append(v_dict)
            
        return jsonify({'vendors': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors', methods=['POST'])
@admin_required
def create_vendor():
    """Create new vendor"""
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400
            
        vendor_id = str(uuid.uuid4())
        vendor = Vendor(
            id=vendor_id,
            name=data['name'],
            email=data.get('email'),
            phone=data.get('phone'),
            description=data.get('description'),
            website=data.get('website'),
            logo_url=data.get('logoUrl'),
            country_code=data.get('countryCode', 'US'),
            status='active',
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(vendor)
        log_audit('VENDOR_CREATE', 'vendor', vendor_id, {'name': data['name']})
        db.session.commit()
        
        return jsonify({'ok': True, 'id': vendor_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>', methods=['GET'])
@admin_required
def get_vendor(vendor_id):
    """Get full vendor details"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        
        # Get active key count
        key_count = VendorAPIKey.query.filter_by(vendor_id=vendor_id, is_active=True).count()
        webhook_count = VendorCustomAPI.query.filter_by(vendor_id=vendor_id, is_active=True).count()
        
        return jsonify({
            'id': vendor.id,
            'name': vendor.name,
            'email': vendor.email,
            'phone': vendor.phone,
            'description': vendor.description,
            'website': vendor.website,
            'logoUrl': vendor.logo_url,
            'status': vendor.status,
            'countryCode': vendor.country_code,
            'createdAt': vendor.created_at.isoformat() if vendor.created_at else None,
            'stats': {
                'activeKeys': key_count,
                'webhooks': webhook_count
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>', methods=['PATCH'])
@admin_required
def update_vendor(vendor_id):
    """Update vendor"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        data = request.get_json()
        
        changes = []
        if 'name' in data:
            vendor.name = data['name']
            changes.append('name')
        if 'email' in data:
            vendor.email = data['email']
        if 'status' in data:
            vendor.status = data['status']
            changes.append(f"status->{data['status']}")
        if 'website' in data:
            vendor.website = data['website']
        if 'description' in data:
            vendor.description = data['description']
        if 'logoUrl' in data:
            vendor.logo_url = data['logoUrl']
            
        vendor.updated_at = datetime.now(timezone.utc)
        log_audit('VENDOR_UPDATE', 'vendor', vendor_id, {'changes': changes})
        db.session.commit()
        
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>', methods=['DELETE'])
@admin_required
def delete_vendor(vendor_id):
    """Suspend vendor (Soft Delete)"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        vendor.status = 'suspended'
        vendor.updated_at = datetime.now(timezone.utc)
        
        # Also deactivate keys?
        # keys = VendorAPIKey.query.filter_by(vendor_id=vendor_id).all()
        # for k in keys: k.is_active = False
        
        log_audit('VENDOR_SUSPEND', 'vendor', vendor_id)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==========================================
# API Keys Management
# ==========================================

@vendors_bp.route('/vendors/<vendor_id>/api-keys', methods=['GET'])
@admin_required
def get_api_keys(vendor_id):
    try:
        keys = VendorAPIKey.query.filter_by(vendor_id=vendor_id).order_by(VendorAPIKey.created_at.desc()).all()
        results = [{
            'id': k.id,
            'keyName': k.key_name,
            'apiKey': k.api_key[:8] + '...' if k.api_key else '???', # Mask public key just in case, though it is public
            'permissions': k.permissions,
            'isActive': k.is_active,
            'createdAt': k.created_at.isoformat() if k.created_at else None,
            'lastUsedAt': k.last_used_at.isoformat() if k.last_used_at else None
        } for k in keys]
        return jsonify({'keys': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/api-keys', methods=['POST'])
@admin_required
def create_api_key(vendor_id):
    """Generate new API Key pair"""
    try:
        data = request.get_json()
        key_name = data.get('keyName', 'Default Key')
        permissions = data.get('permissions', []) # List of strings e.g. ['read_market', 'write_orders']
        
        # 1. Generate Keys
        # Prefix 'vk_' for vendor key public ID
        public_key = 'vk_' + secrets.token_urlsafe(16)
        # Prefix 'vs_' for vendor secret
        secret_raw = 'vs_' + secrets.token_urlsafe(32)
        
        # 2. Hash Secret
        secret_hash = bcrypt.hashpw(secret_raw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        key_id = str(uuid.uuid4())
        
        new_key = VendorAPIKey(
            id=key_id,
            vendor_id=vendor_id,
            key_name=key_name,
            api_key=public_key,
            secret_key=secret_hash, # Store HASH
            permissions=json.dumps(permissions), # Store as JSON
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(new_key)
        log_audit('VENDOR_KEY_CREATE', 'vendor_api_key', key_id, {'vendor_id': vendor_id})
        db.session.commit()
        
        # RETURN SECRET ONLY ONCE
        return jsonify({
            'ok': True,
            'key': {
                'id': key_id,
                'apiKey': public_key,
                'secretKey': secret_raw, # THE ONLY TIME WE SHOW THIS
                'keyName': key_name,
                'createdAt': new_key.created_at.isoformat()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/api-keys/<key_id>', methods=['DELETE'])
@admin_required
def revoke_api_key(vendor_id, key_id):
    """Revoke (Delete) API Key"""
    try:
        # Verify ownership
        key = VendorAPIKey.query.filter_by(id=key_id, vendor_id=vendor_id).first_or_404()
        
        db.session.delete(key)
        log_audit('VENDOR_KEY_REVOKE', 'vendor_api_key', key_id, {'vendor_id': vendor_id})
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==========================================
# Webhooks / Custom APIs
# ==========================================

@vendors_bp.route('/vendors/<vendor_id>/custom-apis', methods=['GET'])
@admin_required
def get_webhooks(vendor_id):
    try:
        hooks = VendorCustomAPI.query.filter_by(vendor_id=vendor_id).all()
        results = [{
            'id': h.id,
            'endpoint': h.endpoint,
            'method': h.method,
            'isActive': h.is_active,
            'createdAt': h.created_at.isoformat() if h.created_at else None,
            # We don't necessarily send full body/headers in list view, but it's fine for admin
            'headers': h.headers, 
            'bodyTemplate': h.body_template
        } for h in hooks]
        return jsonify({'webhooks': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/custom-apis', methods=['POST'])
@admin_required
def create_webhook(vendor_id):
    try:
        data = request.get_json()
        
        webhook_id = str(uuid.uuid4())
        webhook = VendorCustomAPI(
            id=webhook_id,
            vendor_id=vendor_id,
            endpoint=data['endpoint'],
            method=data.get('method', 'POST'),
            headers=json.dumps(data.get('headers', {})),
            body_template=data.get('bodyTemplate', ''),
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
        
        db.session.add(webhook)
        log_audit('VENDOR_WEBHOOK_CREATE', 'vendor_webhook', webhook_id, {'vendor_id': vendor_id})
        db.session.commit()
        
        return jsonify({'ok': True, 'id': webhook_id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/custom-apis/<webhook_id>', methods=['DELETE'])
@admin_required
def delete_webhook(vendor_id, webhook_id):
    try:
        hook = VendorCustomAPI.query.filter_by(id=webhook_id, vendor_id=vendor_id).first_or_404()
        db.session.delete(hook)
        log_audit('VENDOR_WEBHOOK_DELETE', 'vendor_webhook', webhook_id)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
