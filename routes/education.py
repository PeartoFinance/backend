"""
Education API Routes (Public)
Courses, Instructors, and Learning resources
"""
from flask import Blueprint, jsonify, request
from models import Course, Instructor, CourseModule, UserEnrollment
from models.base import db
from routes.decorators import auth_required

education_bp = Blueprint('education', __name__)


@education_bp.route('/courses', methods=['GET'])
def get_courses():
    """Get all published courses with optional filtering"""
    try:
        category = request.args.get('category')
        level = request.args.get('level')
        is_free = request.args.get('free')
        search = request.args.get('search')
        
        # Determine country filter: header-driven. If no header -> US; if header GLOBAL -> GLOBAL; else only header country
        header_country = request.headers.get('X-User-Country')
        if header_country is None:
            country_filter = (Course.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            country_filter = (Course.country_code == 'GLOBAL') if hc == 'GLOBAL' else (Course.country_code == hc)

        query = Course.query.filter(Course.is_published == True, country_filter)
        
        if category:
            query = query.filter(Course.category == category)
        if level:
            query = query.filter(Course.level == level)
        if is_free == 'true':
            query = query.filter(Course.is_free == True)
        if search:
            query = query.filter(Course.title.ilike(f'%{search}%'))
        
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
                'durationWeeks': c.duration_weeks,
                'price': float(c.price) if c.price else 0,
                'discountPrice': float(c.discount_price) if c.discount_price else None,
                'thumbnailUrl': c.thumbnail_url,
                'isFree': c.is_free,
                'enrollmentCount': c.enrollment_count or 0,
                'rating': float(c.rating) if c.rating else 0,
                'ratingCount': c.rating_count or 0,
                'instructorId': c.instructor_id
            } for c in courses],
            'total': len(courses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_bp.route('/courses/<slug>', methods=['GET'])
def get_course(slug):
    """Get single course by slug with modules"""
    try:
        header_country = request.headers.get('X-User-Country')
        if header_country is None:
            country_filter = (Course.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            country_filter = (Course.country_code == 'GLOBAL') if hc == 'GLOBAL' else (Course.country_code == hc)

        course = Course.query.filter(
            Course.slug == slug,
            Course.is_published == True,
            country_filter
        ).first()
        
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        # Get modules
        modules = CourseModule.query.filter(
            CourseModule.course_id == course.id
        ).order_by(CourseModule.order_index).all()
        
        # Get instructor
        instructor = None
        if course.instructor_id:
            inst = Instructor.query.get(course.instructor_id)
            if inst:
                instructor = {
                    'id': inst.id,
                    'name': inst.name,
                    'title': inst.title,
                    'bio': inst.bio,
                    'avatarUrl': inst.avatar_url,
                    'rating': float(inst.rating) if inst.rating else None
                }
        
        return jsonify({
            'id': course.id,
            'title': course.title,
            'slug': course.slug,
            'description': course.description,
            'longDescription': course.long_description,
            'category': course.category,
            'level': course.level,
            'durationHours': course.duration_hours,
            'durationWeeks': course.duration_weeks,
            'price': float(course.price) if course.price else 0,
            'discountPrice': float(course.discount_price) if course.discount_price else None,
            'thumbnailUrl': course.thumbnail_url,
            'videoUrl': course.video_url,
            'isFree': course.is_free,
            'enrollmentCount': course.enrollment_count or 0,
            'rating': float(course.rating) if course.rating else 0,
            'ratingCount': course.rating_count or 0,
            'requirements': course.requirements or [],
            'whatYouLearn': course.what_you_learn or [],
            'instructor': instructor,
            'modules': [{
                'id': m.id,
                'title': m.title,
                'description': m.description,
                'durationMinutes': m.duration_minutes,
                'isFree': m.is_free
            } for m in modules]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_bp.route('/instructors', methods=['GET'])
def get_instructors():
    """Get all active instructors"""
    try:
        # Apply same header-based country scoping for instructors
        header_country = request.headers.get('X-User-Country')
        if header_country is None:
            instructor_filter = (Instructor.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            instructor_filter = (Instructor.country_code == 'GLOBAL') if hc == 'GLOBAL' else (Instructor.country_code == hc)

        instructors = Instructor.query.filter(
            Instructor.is_active == True,
            instructor_filter
        ).order_by(Instructor.courses_count.desc()).all()
        
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
                'coursesCount': i.courses_count or 0
            } for i in instructors]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get unique course categories"""
    try:
        header_country = request.headers.get('X-User-Country')
        if header_country is None:
            cat_filter = (Course.country_code == 'US')
        else:
            hc = header_country.strip().upper()
            cat_filter = (Course.country_code == 'GLOBAL') if hc == 'GLOBAL' else (Course.country_code == hc)

        categories = db.session.query(Course.category).filter(
            Course.is_published == True,
            Course.category != None,
            cat_filter
        ).distinct().all()
        
        return jsonify({
            'categories': [c[0] for c in categories if c[0]]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@education_bp.route('/my-courses', methods=['GET'])
@auth_required
def get_my_courses():
    """Get authenticated user's enrolled courses with progress"""
    try:
        user_id = request.user_id
        
        # Get user's enrollments with course details
        enrollments = db.session.query(
            UserEnrollment, Course, CourseModule
        ).join(
            Course, UserEnrollment.course_id == Course.id
        ).outerjoin(
            CourseModule, UserEnrollment.current_module_id == CourseModule.id
        ).filter(
            UserEnrollment.user_id == user_id
        ).order_by(
            UserEnrollment.last_activity_at.desc()
        ).all()
        
        courses = []
        for enrollment, course, current_module in enrollments:
            courses.append({
                'enrollmentId': enrollment.id,
                'courseId': course.id,
                'title': course.title,
                'slug': course.slug,
                'thumbnailUrl': course.thumbnail_url,
                'category': course.category,
                'level': course.level,
                'progress': enrollment.progress or 0,
                'status': enrollment.status,
                'currentModule': {
                    'id': current_module.id,
                    'title': current_module.title
                } if current_module else None,
                'enrolledAt': enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
                'lastActivityAt': enrollment.last_activity_at.isoformat() if enrollment.last_activity_at else None
            })
        
        return jsonify({
            'courses': courses,
            'total': len(courses)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
