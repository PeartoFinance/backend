"""
Admin Jobs Routes - Job listings management
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, JobListing
from datetime import datetime

jobs_bp = Blueprint('admin_jobs', __name__)


@jobs_bp.route('/jobs', methods=['GET'])
@permission_required("events_jobs")
def get_jobs():
    """List all job listings (country-filtered)"""
    try:
        country = getattr(request, 'user_country', 'US')
        jobs = JobListing.query.filter(
            (JobListing.country_code == country) | 
            (JobListing.country_code == 'GLOBAL')
        ).order_by(JobListing.created_at.desc()).all()
        return jsonify({
            'jobs': [{
                'id': j.id,
                'title': j.title,
                'department': j.department,
                'location': j.location,
                'type': j.type,
                'description': j.description,
                'requirements': j.requirements,
                'salary_range': j.salary_range,
                'is_remote': j.is_remote,
                'is_active': j.is_active,
                'country_code': j.country_code,
                'created_at': j.created_at.isoformat() if j.created_at else None
            } for j in jobs]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/jobs', methods=['POST'])
@permission_required("events_jobs")
def create_job():
    """Create a job listing"""
    try:
        data = request.get_json()
        job = JobListing(
            title=data['title'],
            department=data.get('department'),
            location=data.get('location'),
            type=data.get('type', 'full-time'),
            description=data.get('description'),
            requirements=data.get('requirements'),
            salary_range=data.get('salary_range'),
            is_remote=data.get('is_remote', False),
            is_active=data.get('is_active', True),
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(job)
        db.session.commit()
        return jsonify({'ok': True, 'id': job.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/jobs/<int:id>', methods=['PUT', 'PATCH'])
@permission_required("events_jobs")
def update_job(id):
    """Update a job listing"""
    try:
        job = JobListing.query.get_or_404(id)
        data = request.get_json()
        for key in ['title', 'department', 'location', 'type', 'description', 
                    'requirements', 'salary_range', 'is_remote', 'is_active', 'country_code']:
            if key in data:
                setattr(job, key, data[key])
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@jobs_bp.route('/jobs/<int:id>', methods=['DELETE'])
@permission_required("events_jobs")
def delete_job(id):
    """Delete a job listing"""
    try:
        job = JobListing.query.get_or_404(id)
        db.session.delete(job)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
