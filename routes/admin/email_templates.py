"""
Admin Email Template Routes
CRUD for /api/admin/email-templates
"""
from flask import Blueprint, jsonify, request
from datetime import datetime
from ..decorators import admin_required, permission_required
from models import db
from models.settings import EmailTemplate

# Default template data (from email_service.py TEMPLATES)
DEFAULT_TEMPLATES = [
    {
        'id': 'signup',
        'name': 'Welcome / Signup',
        'description': 'Sent when a new user registers',
        'variables': ['user_name', 'user_email', 'app_name', 'login_url']
    },
    {
        'id': 'login',
        'name': 'Login Notification',
        'description': 'Sent when user logs in from new device',
        'variables': ['user_name', 'login_time', 'device_info', 'ip_address', 'security_url']
    },
    {
        'id': 'forgot_password',
        'name': 'Password Reset',
        'description': 'Sent when user requests password reset',
        'variables': ['user_name', 'reset_url']
    },
    {
        'id': 'verification_code',
        'name': 'Email Verification',
        'description': 'Sent with verification code',
        'variables': ['user_name', 'code']
    },
    {
        'id': 'profile_update',
        'name': 'Profile Updated',
        'description': 'Sent when profile is modified',
        'variables': ['user_name', 'changed_fields']
    },
    {
        'id': 'google_login',
        'name': 'Google Sign-in',
        'description': 'Sent on Google OAuth login',
        'variables': ['user_name', 'login_time', 'device_info', 'ip_address', 'security_url']
    },
]

email_templates_bp = Blueprint('admin_email_templates', __name__)


@email_templates_bp.route('/email-templates', methods=['GET'])
@permission_required("communications")
def get_email_templates():
    """List all email templates"""
    try:
        templates = EmailTemplate.query.all()
        
        # Map DB templates by ID
        db_templates = {t.id: t for t in templates}
        
        result = []
        for default in DEFAULT_TEMPLATES:
            db_tpl = db_templates.get(default['id'])
            result.append({
                'id': default['id'],
                'name': default['name'],
                'description': default['description'],
                'variables': default['variables'],
                'subject': db_tpl.subject if db_tpl else None,
                'body_html': db_tpl.body_html if db_tpl else None,
                'body_text': db_tpl.body_text if db_tpl else None,
                'is_active': db_tpl.is_active if db_tpl else True,
                'is_customized': db_tpl is not None,
                'updated_at': db_tpl.updated_at.isoformat() if db_tpl and db_tpl.updated_at else None
            })
        
        return jsonify({'templates': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_templates_bp.route('/email-templates/<template_id>', methods=['GET'])
@permission_required("communications")
def get_email_template(template_id):
    """Get single email template with defaults"""
    try:
        # Find default template info
        default = next((t for t in DEFAULT_TEMPLATES if t['id'] == template_id), None)
        if not default:
            return jsonify({'error': 'Template not found'}), 404
        
        # Get DB template if exists
        db_tpl = EmailTemplate.query.get(template_id)
        
        # Get hardcoded template for fallback
        from notifications.email_service import TEMPLATES
        hardcoded = TEMPLATES.get(template_id, {})
        
        return jsonify({
            'id': template_id,
            'name': default['name'],
            'description': default['description'],
            'variables': default['variables'],
            'subject': db_tpl.subject if db_tpl else hardcoded.get('subject', ''),
            'body_html': db_tpl.body_html if db_tpl else hardcoded.get('html', ''),
            'body_text': db_tpl.body_text if db_tpl else hardcoded.get('text', ''),
            'is_active': db_tpl.is_active if db_tpl else True,
            'is_customized': db_tpl is not None,
            'default_subject': hardcoded.get('subject', ''),
            'default_html': hardcoded.get('html', ''),
            'default_text': hardcoded.get('text', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@email_templates_bp.route('/email-templates/<template_id>', methods=['PUT'])
@permission_required("communications")
def update_email_template(template_id):
    """Update email template"""
    try:
        data = request.get_json()
        
        # Find or create template
        template = EmailTemplate.query.get(template_id)
        if not template:
            # Find default info
            default = next((t for t in DEFAULT_TEMPLATES if t['id'] == template_id), None)
            if not default:
                return jsonify({'error': 'Template not found'}), 404
            
            template = EmailTemplate(
                id=template_id,
                name=default['name'],
                variables=default['variables']
            )
            db.session.add(template)
        
        # Update fields
        if 'subject' in data:
            template.subject = data['subject']
        if 'body_html' in data:
            template.body_html = data['body_html']
        if 'body_text' in data:
            template.body_text = data['body_text']
        if 'is_active' in data:
            template.is_active = data['is_active']
        
        template.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'ok': True, 'message': 'Template updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_templates_bp.route('/email-templates/<template_id>/reset', methods=['POST'])
@permission_required("communications")
def reset_email_template(template_id):
    """Reset template to default (delete DB customization)"""
    try:
        template = EmailTemplate.query.get(template_id)
        if template:
            db.session.delete(template)
            db.session.commit()
        
        return jsonify({'ok': True, 'message': 'Template reset to default'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@email_templates_bp.route('/email-templates/test', methods=['POST'])
@permission_required("communications")
def test_email_template():
    """Send test email with template"""
    try:
        data = request.get_json()
        template_id = data.get('template_id')
        recipient = data.get('recipient')
        
        if not template_id or not recipient:
            return jsonify({'error': 'template_id and recipient are required'}), 400
        
        from notifications.email_service import EmailService
        
        email_service = EmailService()
        
        # Test data for templates
        test_data = {
            'user_name': 'Test User',
            'user_email': recipient,
            'login_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'device_info': 'Test Browser',
            'ip_address': '127.0.0.1',
            'code': '123456',
            'changed_fields': 'Email, Name',
            'reset_url': 'https://example.com/reset?token=test123'
        }
        
        success = email_service.send_email(recipient, template_id, test_data)
        
        if success:
            return jsonify({'ok': True, 'message': f'Test email sent to {recipient}'})
        else:
            return jsonify({'error': 'Failed to send test email'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500
