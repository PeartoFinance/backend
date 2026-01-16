"""
User Documents API Routes
Document upload and management for KYC
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import uuid
import os
from routes.decorators import auth_required
from models import db, UserDocument

documents_bp = Blueprint('documents', __name__)

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads/documents')


@documents_bp.route('', methods=['GET'])
@auth_required
def get_documents():
    """Get all user documents"""
    documents = UserDocument.query.filter_by(user_id=request.user.id).order_by(UserDocument.created_at.desc()).all()
    
    return jsonify([{
        'id': d.id,
        'documentType': d.document_type,
        'fileUrl': d.file_url,
        'status': d.status,
        'reviewedAt': d.reviewed_at.isoformat() if d.reviewed_at else None,
        'notes': d.notes,
        'createdAt': d.created_at.isoformat() if d.created_at else None
    } for d in documents])


@documents_bp.route('', methods=['POST'])
@auth_required
def upload_document():
    """Upload a new document"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    document_type = request.form.get('documentType', 'other')
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Generate unique filename
    ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else 'bin'
    filename = f"{uuid.uuid4()}.{ext}"
    
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Save file
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Create document record
    doc = UserDocument(
        id=str(uuid.uuid4()),
        user_id=request.user.id,
        document_type=document_type,
        file_url=f"/uploads/documents/{filename}",
        status='approved'
    )
    
    db.session.add(doc)
    db.session.commit()
    
    # Track document upload activity
    try:
        from handlers import track_document_upload
        track_document_upload(request.user.id, doc.id, document_type)
    except Exception as e:
        print(f'[Documents] Activity tracking failed: {e}')
    
    return jsonify({
        'id': doc.id,
        'message': 'Document uploaded successfully'
    }), 201


@documents_bp.route('/<doc_id>', methods=['DELETE'])
@auth_required
def delete_document(doc_id):
    """Delete a document"""
    doc = UserDocument.query.filter_by(id=doc_id, user_id=request.user.id).first()
    if not doc:
        return jsonify({'error': 'Document not found'}), 404
    
    # Only allow deletion of pending documents
    if doc.status != 'pending':
        return jsonify({'error': 'Cannot delete reviewed documents'}), 400
    
    db.session.delete(doc)
    db.session.commit()
    
    return jsonify({'message': 'Document deleted'})
