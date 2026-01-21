"""
Backup & Restore API Routes
PeartoFinance Backend

This file defines the API endpoints for exporting and importing user data.
It uses the BackupService to perform the actual data processing.

Routes:
- GET /api/backup/export: Generates and downloads a JSON backup.
- POST /api/backup/import: Uploads and restores data from a JSON backup.
"""

from flask import Blueprint, request, jsonify, send_file
import json
import io
from datetime import datetime
from .decorators import auth_required
from services.backup_service import BackupService

backup_bp = Blueprint('backup', __name__)

@backup_bp.route('/export', methods=['GET'])
@auth_required
def export_data():
    """
    Export all user data as a JSON file.
    Usage: GET /api/backup/export
    Authorization: Bearer <token>
    """
    user = request.user
    
    # 1. Generate the backup dictionary using the service
    backup_dict = BackupService.export_user_data(user.id)
    
    if not backup_dict:
        return jsonify({'error': 'Failed to generate backup'}), 500

    # 2. Convert dictionary to a JSON string
    json_data = json.dumps(backup_dict, indent=2)
    
    # 3. Create a file-like object in memory
    buffer = io.BytesIO()
    buffer.write(json_data.encode('utf-8'))
    buffer.seek(0)
    
    # 4. Generate a filename with the current date
    filename = f"pearto_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 5. Send the file to the browser
    return send_file(
        buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/json'
    )

@backup_bp.route('/import', methods=['POST'])
@auth_required
def import_data():
    """
    Import user data from a JSON file.
    Usage: POST /api/backup/import (Multipart/form-data with 'file' field)
    Authorization: Bearer <token>
    """
    user = request.user
    
    # 1. Check if a file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only .json files are allowed'}), 400

    try:
        # 2. Read and parse the JSON file
        file_content = file.read().decode('utf-8')
        data = json.loads(file_content)
        
        # 3. Use the service to restore the data
        success, message = BackupService.import_user_data(user.id, data)
        
        if success:
            return jsonify({
                'success': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'error': message
            }), 400

    except json.JSONDecodeError:
        return jsonify({'error': 'Invalid JSON format'}), 400
    except Exception as e:
        return jsonify({'error': f'An unexpected error occurred: {str(e)}'}), 500
