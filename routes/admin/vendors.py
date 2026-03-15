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
from models import db, Vendor, VendorAPIKey, VendorCustomAPI, AuditEvent, VendorReview, VendorHistory
from ..decorators import admin_required, permission_required

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
@permission_required("vendors_manage")
def get_vendors():
    """List all vendors"""
    try:
        vendors = Vendor.query.order_by(Vendor.created_at.desc()).all()
        results = []
        for v in vendors:
            v_dict = {
                'id': v.id,
                'name': v.name,
                'email': v.email,
                'category': v.category,
                'rating': float(v.rating) if v.rating else 0,
                'isFeatured': v.is_featured,
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
@permission_required("vendors_manage")
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
            category=data.get('category'),
            services=data.get('services', []),
            is_featured=data.get('isFeatured', False),
            metadata_json=data.get('metadata', {}),
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
@permission_required("vendors_manage")
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
            'category': vendor.category,
            'services': vendor.services,
            'rating': float(vendor.rating) if vendor.rating else 0,
            'reviewCount': vendor.review_count,
            'isFeatured': vendor.is_featured,
            'metadata': vendor.metadata_json or {},
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
@permission_required("vendors_manage")
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
        if 'category' in data:
            vendor.category = data['category']
        if 'services' in data:
            vendor.services = data['services']
        if 'isFeatured' in data:
            vendor.is_featured = data['isFeatured']
        if 'metadata' in data:
            vendor.metadata_json = data['metadata']
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
@permission_required("vendors_manage")
def delete_vendor(vendor_id):
    """Suspend vendor (Soft Delete)"""
    try:
        vendor = Vendor.query.get_or_404(vendor_id)
        vendor.status = 'suspended'
        vendor.updated_at = datetime.now(timezone.utc)
        
        # Deactivate all API keys on suspend
        keys = VendorAPIKey.query.filter_by(vendor_id=vendor_id).all()
        deactivated_count = 0
        for k in keys:
            if k.is_active:
                k.is_active = False
                deactivated_count += 1
        
        log_audit('VENDOR_SUSPEND', 'vendor', vendor_id, {'keys_deactivated': deactivated_count})
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==========================================
# API Keys Management
# ==========================================

@vendors_bp.route('/vendors/<vendor_id>/api-keys', methods=['GET'])
@permission_required("vendors_manage")
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
@permission_required("vendors_manage")
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
            permissions=permissions, # JSON column handles serialization
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

@vendors_bp.route('/vendors/<vendor_id>/api-keys/<key_id>', methods=['PATCH'])
@permission_required("vendors_manage")
def toggle_api_key(vendor_id, key_id):
    """Toggle API Key active status or update permissions"""
    try:
        key = VendorAPIKey.query.filter_by(id=key_id, vendor_id=vendor_id).first_or_404()
        data = request.get_json()
        
        if 'isActive' in data:
            key.is_active = data['isActive']
        if 'permissions' in data:
            key.permissions = data['permissions']
        if 'keyName' in data:
            key.key_name = data['keyName']
            
        log_audit('VENDOR_KEY_UPDATE', 'vendor_api_key', key_id, {'vendor_id': vendor_id, 'changes': list(data.keys())})
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/api-keys/<key_id>', methods=['DELETE'])
@permission_required("vendors_manage")
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
@permission_required("vendors_manage")
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
@permission_required("vendors_manage")
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

@vendors_bp.route('/vendors/<vendor_id>/custom-apis/<webhook_id>', methods=['PATCH'])
@permission_required("vendors_manage")
def update_webhook(vendor_id, webhook_id):
    """Update webhook configuration"""
    try:
        hook = VendorCustomAPI.query.filter_by(id=webhook_id, vendor_id=vendor_id).first_or_404()
        data = request.get_json()
        
        if 'endpoint' in data:
            hook.endpoint = data['endpoint']
        if 'method' in data:
            hook.method = data['method']
        if 'headers' in data:
            hook.headers = json.dumps(data['headers']) if isinstance(data['headers'], dict) else data['headers']
        if 'bodyTemplate' in data:
            hook.body_template = data['bodyTemplate']
        if 'isActive' in data:
            hook.is_active = data['isActive']
            
        log_audit('VENDOR_WEBHOOK_UPDATE', 'vendor_webhook', webhook_id, {'vendor_id': vendor_id})
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/custom-apis/<webhook_id>', methods=['DELETE'])
@permission_required("vendors_manage")
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

# ==========================================
# Reviews Management
# ==========================================

@vendors_bp.route('/vendors/<vendor_id>/reviews', methods=['GET'])
@permission_required("vendors_manage")
def get_admin_reviews(vendor_id):
    try:
        reviews = VendorReview.query.filter_by(vendor_id=vendor_id).order_by(VendorReview.created_at.desc()).all()
        results = [{
            'id': r.id,
            'userName': r.user.name if r.user else 'Anonymous',
            'rating': r.rating,
            'comment': r.comment,
            'date': r.created_at.isoformat(),
            'isVerified': r.is_verified_customer
        } for r in reviews]
        return jsonify({'reviews': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/reviews/<review_id>', methods=['DELETE'])
@permission_required("vendors_manage")
def delete_review(review_id):
    try:
        review = VendorReview.query.get_or_404(review_id)
        vendor_id = review.vendor_id
        db.session.delete(review)
        
        # Update vendor rating stats
        # Recalculate average
        remaining = VendorReview.query.filter_by(vendor_id=vendor_id).all()
        if remaining:
            avg = sum(r.rating for r in remaining) / len(remaining)
            count = len(remaining)
        else:
            avg = 0
            count = 0
            
        vendor = Vendor.query.get(vendor_id)
        if vendor:
            vendor.rating = avg
            vendor.review_count = count
            
        log_audit('VENDOR_REVIEW_DELETE', 'vendor_review', review_id)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# ==========================================
# History / Analytics Management
# ==========================================

@vendors_bp.route('/vendors/<vendor_id>/history', methods=['GET'])
@permission_required("vendors_manage")
def get_admin_history(vendor_id):
    try:
        # Group by date for the UI
        history = VendorHistory.query.filter_by(vendor_id=vendor_id).order_by(VendorHistory.recorded_at.desc()).all()
        
        # Grouping
        grouped = {}
        for h in history:
            date_str = h.recorded_at.date().isoformat()
            if date_str not in grouped:
                grouped[date_str] = {
                    'id': date_str, # Use date as group ID
                    'date': h.recorded_at.isoformat(),
                    'metrics': {},
                    'entryIds': {}
                }
            grouped[date_str]['metrics'][h.metric_type] = float(h.value)
            grouped[date_str]['entryIds'][h.metric_type] = h.id
            
        results = list(grouped.values())
        return jsonify({'history': results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/history', methods=['POST'])
@permission_required("vendors_manage")
def add_history_point(vendor_id):
    try:
        data = request.get_json()
        date_str = data.get('date') # YYYY-MM-DD
        metrics = data.get('metrics', {})
        
        if not date_str or not metrics:
            return jsonify({'error': 'Date and metrics required'}), 400
            
        # Parse date
        recorded_at = datetime.fromisoformat(date_str.replace('Z', '+00:00')) if 'T' in date_str else datetime.strptime(date_str, '%Y-%m-%d')
        
        created_ids = []
        
        for key, val in metrics.items():
            # Validate value is number
            try:
                numeric_val = float(val)
            except:
                continue
                
            entry_id = str(uuid.uuid4()) # actually VendorHistory uses int ID auth-increment, let's omit ID
            # But wait, model says: id = db.Column(db.Integer, primary_key=True, autoincrement=True)
            
            entry = VendorHistory(
                vendor_id=vendor_id,
                metric_type=key,
                value=numeric_val,
                recorded_at=recorded_at
            )
            db.session.add(entry)
            created_ids.append(key)
            
        log_audit('VENDOR_HISTORY_ADD', 'vendor_history', vendor_id, {'metrics': created_ids})
        db.session.commit()
        return jsonify({'ok': True, 'count': len(created_ids)}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/history/<int:entry_id>', methods=['DELETE'])
@permission_required("vendors_manage")
def delete_history_point(vendor_id, entry_id):
    """Delete a single history data point"""
    try:
        entry = VendorHistory.query.filter_by(id=entry_id, vendor_id=vendor_id).first_or_404()
        db.session.delete(entry)
        log_audit('VENDOR_HISTORY_DELETE', 'vendor_history', str(entry_id), {'vendor_id': vendor_id})
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@vendors_bp.route('/vendors/<vendor_id>/history/batch-delete', methods=['POST'])
@permission_required("vendors_manage")
def delete_history_batch(vendor_id):
    """Delete all history points for a given date"""
    try:
        data = request.get_json()
        date_str = data.get('date')
        if not date_str:
            return jsonify({'error': 'Date required'}), 400
            
        target_date = datetime.strptime(date_str[:10], '%Y-%m-%d').date()
        
        entries = VendorHistory.query.filter_by(vendor_id=vendor_id).all()
        deleted = 0
        for e in entries:
            if e.recorded_at.date() == target_date:
                db.session.delete(e)
                deleted += 1
        
        log_audit('VENDOR_HISTORY_BATCH_DELETE', 'vendor_history', vendor_id, {'date': date_str, 'deleted': deleted})
        db.session.commit()
        return jsonify({'ok': True, 'deleted': deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
