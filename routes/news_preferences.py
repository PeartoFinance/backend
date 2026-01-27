"""
News Preferences API Routes
Handles user news preferences (companies, categories, news type)
"""
from flask import Blueprint, request, jsonify
from models import NewsPreference, User
from models.base import db
from datetime import datetime, timezone
from .decorators import auth_required

news_prefs_bp = Blueprint('news_prefs', __name__)

# ==================== GET User News Preferences ====================
@news_prefs_bp.route('', methods=['GET'])
@auth_required
def get_news_preferences():
    """
    GET user's news preferences
    Returns: companies, categories, news_type
    """
    user = request.user

    try:
        prefs = NewsPreference.query.filter_by(user_id = user.id).first()
        if not prefs:
            # Empty state is NOT an error
            return jsonify({
                'userId': user.id,
                'companies': [],
                'categories': [],
                'newsType': None,
                'createdAt': None,
                'updatedAt': None,
            }), 200
        
        return jsonify({
            'id': prefs.id,
            'userId': prefs.user_id,
            'companies': prefs.companies or [],
            'categories': prefs.categories or [],
            'newsType': prefs.news_type,
            'createdAt': prefs.created_at.isoformat() if prefs.created_at else None,
            'updatedAt': prefs.updated_at.isoformat() if prefs.updated_at else None,
        }), 200
    except Exception as e:
        return jsonify({'error':str(e)}), 500

    
# ==================== CREATE News Preferences ====================
@news_prefs_bp.route('', methods=['POST'])
@auth_required
def create_news_preferences():
    """
    POST create user news preferences
    Body: {companies, categories, news_type}
    """
    user  =request.user

    try:
        # check user exists
        user = User.query.filter_by(id = user.id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # check preferences exists
        prefs = NewsPreference.query.filter_by(user_id = user.id).first()
        if prefs:
            return jsonify({'error': 'News preferences already exists'}), 400

        data = request.get_json()

        # Validate request body
        if not data:
            return jsonify({'error':'Request body is missing'}), 400
        
        companies = data.get('companies', [])
        categories = data.get('categories', [])
        news_type = data.get('newsType')

        # Validate companies and categories are lists
        if not isinstance(companies, list) or not isinstance(categories, list):
            return jsonify({'error': 'Companies and categories must be lists'}), 400

        # Validate news_type is provided and valid enum
        if news_type is None:
            return jsonify({'error': 'newsType is required and must be "company" or "independent"'}), 400
        if news_type not in ['company', 'independent']:
            return jsonify({'error': 'newsType must be "company" or "independent"'}), 400
        
        # create preferences
        prefs = NewsPreference(
            user_id = user.id,
            companies = data.get('companies', []),
            categories = data.get('categories', []),
            news_type = data.get('newsType'),
            created_at = datetime.now(timezone.utc),
            updated_at = datetime.now(timezone.utc)
        )
        db.session.add(prefs)
        db.session.commit()
        
        return jsonify({
            'id': prefs.id,
            'userId': prefs.user_id,
            'companies': prefs.companies or [],
            'categories': prefs.categories or [],
            'newsType': prefs.news_type,
            'createdAt': prefs.created_at.isoformat() if prefs.created_at else None,
            'updatedAt': prefs.updated_at.isoformat() if prefs.updated_at else None,
            'message': 'News preferences created successfully'
        }), 201
   
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

# ==================== UPDATE News Preferences ====================
@news_prefs_bp.route('', methods=['PUT'])
@auth_required
def update_news_preferences():
    """
    PUT update user news preferences
    Body: {companies, categories, news_type}
    """
    user = request.user
    
    try:
        # check user exists
        user = User.query.filter_by(id = user.id).first()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # check preferences exists
        prefs = NewsPreference.query.filter_by(user_id = user.id).first()
        if not prefs:
            return jsonify({'error': 'News preferences not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is missing'}), 400
        
        # update only provided fields
        if 'companies' in data:
            if not isinstance(data['companies'], list):
                return jsonify({'error': 'companies must be a list'}), 400
            prefs.companies = data['companies']
        
        if 'categories' in data:
            if not isinstance(data['categories'], list):
                return jsonify({'error': 'categories must be a list'}), 400
            prefs.categories = data['categories']
        
        if 'newsType' in data:
            if data['newsType'] not in ['company', 'independent']:
                return jsonify({'error': 'newsType must be "company" or "independent"'}), 400
            prefs.news_type = data['newsType']
        
        prefs.updated_at = datetime.now(timezone.utc)

        db.session.commit()
        return jsonify({
            'id': prefs.id,
            'userId': prefs.user_id,
            'companies': prefs.companies,
            'categories': prefs.categories,
            'newsType': prefs.news_type,
            'createdAt': prefs.created_at.isoformat(),
            'updatedAt': prefs.updated_at.isoformat(),
            'message': 'Preferences updated successfully'
        }), 200
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    

# ==================== DELETE News Preferences ====================
@news_prefs_bp.route('', methods=['DELETE'])
@auth_required
def delete_news_preferences():
    """
    DELETE user news preferences
    """
    user_id = request.headers.get('X-User-ID')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 401
    
    try:
        user_id = int(user_id)
        
        # Find and delete preferences
        prefs = NewsPreference.query.filter_by(user_id=user_id).first()
        if not prefs:
            return jsonify({'error': 'No preferences found'}), 404
        
        db.session.delete(prefs)
        db.session.commit()
        
        return jsonify({'message': 'Preferences deleted successfully'}), 200
    
    except ValueError:
        return jsonify({'error': 'Invalid user ID format'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
        
