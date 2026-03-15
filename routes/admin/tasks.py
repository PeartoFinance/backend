"""
Admin Tasks Routes - Task management
With country-specific filtering
"""
from flask import Blueprint, jsonify, request
from ..decorators import admin_required, permission_required
from models import db, Task
from datetime import datetime
import uuid

tasks_bp = Blueprint('admin_tasks', __name__)


@tasks_bp.route('/tasks', methods=['GET'])
@permission_required("system_tasks")
def get_tasks():
    """List all tasks (country-filtered)"""
    try:
        status = request.args.get('status')
        country = getattr(request, 'user_country', 'US')
        query = Task.query.filter(
            (Task.country_code == country) | (Task.country_code == 'GLOBAL')
        ).order_by(Task.created_at.desc())
        if status:
            query = query.filter(Task.status == status)
        tasks = query.limit(500).all()
        return jsonify({
            'tasks': [{
                'id': t.id,
                'title': t.title,
                'description': t.description,
                'status': t.status,
                'priority': t.priority,
                'due_date': t.due_date.isoformat() if t.due_date else None,
                'country_code': t.country_code,
                'created_at': t.created_at.isoformat() if t.created_at else None,
                'completed_at': t.completed_at.isoformat() if t.completed_at else None
            } for t in tasks]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/tasks/<id>', methods=['GET'])
@permission_required("system_tasks")
def get_task(id):
    """Get a task detail by id"""
    try:
        task = Task.query.get_or_404(id)
        return jsonify({
            'task': {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'status': task.status,
                'priority': task.priority,
                'due_date': task.due_date.isoformat() if task.due_date else None,
                'country_code': task.country_code,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks', methods=['POST'])
@permission_required("system_tasks")
def create_task():
    """Create a task"""
    try:
        data = request.get_json()
        task = Task(
            id=str(uuid.uuid4()),
            title=data['title'],
            description=data.get('description'),
            status=data.get('status', 'pending'),
            priority=data.get('priority', 'medium'),
            due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
            country_code=data.get('country_code', getattr(request, 'user_country', 'US'))
        )
        db.session.add(task)
        db.session.commit()
        return jsonify({'ok': True, 'id': task.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<id>', methods=['PUT', 'PATCH'])
@permission_required("system_tasks")
def update_task(id):
    """Update a task"""
    try:
        task = Task.query.get_or_404(id)
        data = request.get_json()
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'status' in data:
            task.status = data['status']
            if data['status'] == 'completed':
                task.completed_at = datetime.utcnow()
        if 'country_code' in data:
            task.country_code = data['country_code']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = datetime.fromisoformat(data['due_date']) if data['due_date'] else None
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@tasks_bp.route('/tasks/<id>', methods=['DELETE'])
@permission_required("system_tasks")
def delete_task(id):
    """Delete a task"""
    try:
        task = Task.query.get_or_404(id)
        db.session.delete(task)
        db.session.commit()
        return jsonify({'ok': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
