"""
Admin Education Routes (CRUD for Courses, Instructors)
"""
from flask import Blueprint, jsonify, request
from models import Course, Instructor, CourseModule
from models.base import db
from routes.admin.country_filter import get_country_context, apply_country_filter

education_admin_bp = Blueprint('education_admin', __name__, url_prefix='/api/admin/education')


def require_admin():
    """Simple admin auth check"""
    secret = request.headers.get('X-Admin-Secret')
    import os
    if secret != os.getenv('ADMIN_SECRET_KEY', 'pearto-admin-secret-2024'):
        return False
    return True


# ===== COURSES =====

@education_admin_bp.route('/courses', methods=['GET'])
def list_courses():
    """List all courses with filtering"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        country, is_global = get_country_context(request)
        query = Course.query
        
        if not is_global:
            query = apply_country_filter(query, Course, country)
        
        courses = query.order_by(Course.created_at.desc()).all()
        
        return jsonify({
            'courses': [{
                'id': c.id,
                'title': c.title,
                'slug': c.slug,
                'description': c.description,
                'category': c.category,
                'level': c.level,
                'durationHours': c.duration_hours,
                'price': float(c.price) if c.price else 0,
                'thumbnailUrl': c.thumbnail_url,
                'isPublished': c.is_published,
                'isFree': c.is_free,
                'enrollmentCount': c.enrollment_count or 0,
                'rating': float(c.rating) if c.rating else 0,
                'countryCode': c.country_code,
                'createdAt': c.created_at.isoformat() if c.created_at else None
            } for c in courses],
            'total': len(courses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/courses', methods=['POST'])
def create_course():
    """Create a new course"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        country, _ = get_country_context(request)
        
        course = Course(
            title=data.get('title'),
            slug=data.get('slug') or data.get('title', '').lower().replace(' ', '-'),
            description=data.get('description'),
            long_description=data.get('longDescription'),
            category=data.get('category'),
            level=data.get('level', 'Beginner'),
            duration_hours=data.get('durationHours'),
            duration_weeks=data.get('durationWeeks'),
            price=data.get('price', 0),
            discount_price=data.get('discountPrice'),
            thumbnail_url=data.get('thumbnailUrl'),
            video_url=data.get('videoUrl'),
            is_published=data.get('isPublished', False),
            is_free=data.get('isFree', False),
            instructor_id=data.get('instructorId'),
            requirements=data.get('requirements'),
            what_you_learn=data.get('whatYouLearn'),
            country_code=data.get('countryCode') or country
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'id': course.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
def update_course(course_id):
    """Update a course"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        data = request.get_json()
        
        for field in ['title', 'slug', 'description', 'category', 'level', 'thumbnail_url', 'video_url']:
            if field in data or field.replace('_', '') in data:
                camel = ''.join(x.title() for x in field.split('_'))
                camel = camel[0].lower() + camel[1:]
                setattr(course, field, data.get(camel) or data.get(field))
        
        if 'price' in data:
            course.price = data['price']
        if 'durationHours' in data:
            course.duration_hours = data['durationHours']
        if 'isPublished' in data:
            course.is_published = data['isPublished']
        if 'isFree' in data:
            course.is_free = data['isFree']
        if 'longDescription' in data:
            course.long_description = data['longDescription']
        
        db.session.commit()
        return jsonify({'message': 'Course updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/courses/<int:course_id>', methods=['DELETE'])
def delete_course(course_id):
    """Delete a course"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        db.session.delete(course)
        db.session.commit()
        return jsonify({'message': 'Course deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== INSTRUCTORS =====

@education_admin_bp.route('/instructors', methods=['GET'])
def list_instructors():
    """List all instructors"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        country, is_global = get_country_context(request)
        query = Instructor.query
        
        if not is_global:
            query = apply_country_filter(query, Instructor, country)
        
        instructors = query.order_by(Instructor.name).all()
        
        return jsonify({
            'instructors': [{
                'id': i.id,
                'name': i.name,
                'title': i.title,
                'bio': i.bio,
                'avatarUrl': i.avatar_url,
                'expertise': i.expertise,
                'rating': float(i.rating) if i.rating else 0,
                'studentsTaught': i.students_taught or 0,
                'coursesCount': i.courses_count or 0,
                'isActive': i.is_active,
                'countryCode': i.country_code
            } for i in instructors]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/instructors', methods=['POST'])
def create_instructor():
    """Create a new instructor"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        country, _ = get_country_context(request)
        
        instructor = Instructor(
            name=data.get('name'),
            title=data.get('title'),
            bio=data.get('bio'),
            avatar_url=data.get('avatarUrl'),
            expertise=data.get('expertise'),
            is_active=data.get('isActive', True),
            country_code=data.get('countryCode') or country
        )
        
        db.session.add(instructor)
        db.session.commit()
        
        return jsonify({
            'message': 'Instructor created successfully',
            'id': instructor.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/instructors/<int:instructor_id>', methods=['PUT'])
def update_instructor(instructor_id):
    """Update an instructor"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        data = request.get_json()
        
        if 'name' in data:
            instructor.name = data['name']
        if 'title' in data:
            instructor.title = data['title']
        if 'bio' in data:
            instructor.bio = data['bio']
        if 'avatarUrl' in data:
            instructor.avatar_url = data['avatarUrl']
        if 'expertise' in data:
            instructor.expertise = data['expertise']
        if 'isActive' in data:
            instructor.is_active = data['isActive']
        
        db.session.commit()
        return jsonify({'message': 'Instructor updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/instructors/<int:instructor_id>', methods=['DELETE'])
def delete_instructor(instructor_id):
    """Delete an instructor"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        instructor = Instructor.query.get(instructor_id)
        if not instructor:
            return jsonify({'error': 'Instructor not found'}), 404
        
        db.session.delete(instructor)
        db.session.commit()
        return jsonify({'message': 'Instructor deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===== STATS =====

@education_admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get education stats"""
    if not require_admin():
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        country, is_global = get_country_context(request)
        
        courses_query = Course.query
        instructors_query = Instructor.query
        
        if not is_global:
            courses_query = apply_country_filter(courses_query, Course, country)
            instructors_query = apply_country_filter(instructors_query, Instructor, country)
        
        total_courses = courses_query.count()
        published_courses = courses_query.filter(Course.is_published == True).count()
        total_instructors = instructors_query.count()
        total_enrollments = db.session.query(
            db.func.sum(Course.enrollment_count)
        ).scalar() or 0
        
        return jsonify({
            'totalCourses': total_courses,
            'publishedCourses': published_courses,
            'totalInstructors': total_instructors,
            'totalEnrollments': int(total_enrollments)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
