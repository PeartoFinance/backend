"""
Admin Education Routes (CRUD for Courses, Instructors)
"""
"""
Admin Education Routes

Responsibilities:
- Manage education content (courses, modules, instructors)
- Control visibility and publishing
- Observe enrollment and learning progress (read-only)

Non-responsibilities:
- Modifying user learning state
- Enrolling or unenrolling users
- Updating progress or completion

IMPORTANT:
Admin routes must not bypass learning rules enforced
by user education endpoints.
"""



from flask import Blueprint, jsonify, request
from models import Course, Instructor, CourseModule
from models.base import db
from models.education import UserEnrollment
from models.user import User
from ..decorators import admin_required
from routes.admin.country_filter import get_country_context

education_admin_bp = Blueprint('education_admin', __name__, url_prefix='/education')

# ===== COURSES =====

@education_admin_bp.route('/courses', methods=['GET'])
@admin_required
def list_courses():
    """List all courses with filtering"""
    try:
        is_global, header_country = get_country_context()
        if not is_global and header_country:
            country = header_country
        else:
            country = getattr(request, 'user_country', 'US')

        query = Course.query.filter(
            (Course.country_code == country) | (Course.country_code == 'GLOBAL')
        )

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
@admin_required
def create_course():
    """
    Create one or multiple courses.

    Accepts:
    - Single course payload
    - Batch payload: { "courses": [ {...}, {...} ] }

    Each course is stored as a separate DB row.
    """
    try:
        payload = request.get_json()

        # ---- 1. Normalize input ----
        if isinstance(payload, dict) and 'courses' in payload:
            courses_data = payload.get('courses')
        elif isinstance(payload, dict):
            courses_data = [payload]
        else:
            return jsonify({'error': 'Invalid request payload'}), 400

        if not courses_data:
            return jsonify({'error': 'No courses provided'}), 400

        # Safety guard (recommended)
        if len(courses_data) > 20:
            return jsonify({'error': 'Too many courses in one request'}), 400

        created_courses = []

        # ---- 2. Resolve country context once ----
        is_global, header_country = get_country_context()
        default_country = (
            header_country if not is_global and header_country
            else getattr(request, 'user_country', 'US')
        )

        # ---- 3. Create courses ----
        for index, data in enumerate(courses_data):
            title = data.get('title')
            if not title:
                return jsonify({
                    'error': f'Missing title for course at index {index}'
                }), 400

            instructor_id = data.get('instructorId')
            if instructor_id and not Instructor.query.get(instructor_id):
                return jsonify({
                    'error': f'Instructor does not exist for course at index {index}'
                }), 400

            country = data.get('countryCode') or default_country

            course = Course(
                title=title,
                slug=data.get('slug') or title.lower().replace(' ', '-'),
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
                instructor_id=instructor_id,
                requirements=data.get('requirements'),
                what_you_learn=data.get('whatYouLearn'),
                country_code=country
            )

            db.session.add(course)
            created_courses.append(course)

        # ---- 4. Commit once (atomic) ----
        db.session.commit()

        return jsonify({
            'message': 'Courses created successfully',
            'count': len(created_courses),
            'courses': [
                {'id': c.id, 'title': c.title}
                for c in created_courses
            ]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/courses/<int:course_id>', methods=['PUT'])
@admin_required
def update_course(course_id):
    """Update a course"""
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
@admin_required
def delete_course(course_id):
    """Delete a course"""
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
@admin_required
def list_instructors():
    """List all instructors"""
    try:
        is_global, header_country = get_country_context()
        if not is_global and header_country:
            country = header_country
        else:
            country = getattr(request, 'user_country', 'US')

        query = Instructor.query.filter(
            (Instructor.country_code == country) | (Instructor.country_code == 'GLOBAL')
        )

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
@admin_required
def create_instructor():
    """Create a new instructor"""
    try:
        data = request.get_json()
        payload_country = data.get('countryCode')
        if payload_country:
            country = payload_country
        else:
            is_global, header_country = get_country_context()
            if not is_global and header_country:
                country = header_country
            else:
                country = getattr(request, 'user_country', 'US')
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
@admin_required
def update_instructor(instructor_id):
    """Update an instructor"""
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
@admin_required
def delete_instructor(instructor_id):
    """Delete an instructor"""
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
@admin_required
def get_stats():
    """Get education stats"""
    try:
        is_global, header_country = get_country_context()
        if not is_global and header_country:
            country = header_country
        else:
            country = getattr(request, 'user_country', 'US')

        courses_query = Course.query.filter(
            (Course.country_code == country) | (Course.country_code == 'GLOBAL')
        )
        instructors_query = Instructor.query.filter(
            (Instructor.country_code == country) | (Instructor.country_code == 'GLOBAL')
        )

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


# ============= Modules =============
# Post request to create course modules
@education_admin_bp.route('/courses/<int:course_id>/modules', methods=['POST'])
@admin_required
def create_module(course_id):
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        data = request.get_json()
        title = data.get('title')
        if not title:
            return jsonify({'error': 'Module title is required'}), 400

        # calculate next order index
        max_order = (
            db.session.query(db.func.max(CourseModule.order_index))
            .filter_by(course_id=course_id)
            .scalar()
        ) or 0

        module = CourseModule(
            course_id=course_id,
            title=title,
            description=data.get('description'),
            duration_minutes=data.get('durationMinutes'),
            video_url=data.get('videoUrl'),
            content=data.get('content'),
            is_free=data.get('isFree', False),
            order_index=max_order + 1
        )

        db.session.add(module)
        db.session.commit()

        return jsonify({
            'message': 'Module created successfully',
            'id': module.id,
            'orderIndex': module.order_index
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/courses/<int:course_id>/modules', methods=['GET'])
@admin_required
def list_modules(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    modules = (
        CourseModule.query
        .filter_by(course_id=course_id)
        .order_by(CourseModule.order_index)
        .all()
    )

    return jsonify({
        'modules': [{
            'id': m.id,
            'title': m.title,
            'description': m.description,
            'orderIndex': m.order_index,
            'durationMinutes': m.duration_minutes,
            'isFree': m.is_free
        } for m in modules]
    })



@education_admin_bp.route('/modules/<int:module_id>', methods=['PUT'])
@admin_required
def update_module(module_id):
    try:
        module = CourseModule.query.get(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404

        data = request.get_json()

        if 'title' in data:
            module.title = data['title']
        if 'description' in data:
            module.description = data['description']
        if 'durationMinutes' in data:
            module.duration_minutes = data['durationMinutes']
        if 'videoUrl' in data:
            module.video_url = data['videoUrl']
        if 'content' in data:
            module.content = data['content']
        if 'isFree' in data:
            module.is_free = data['isFree']

        db.session.commit()

        return jsonify({'message': 'Module updated successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@education_admin_bp.route('/modules/<int:module_id>', methods=['DELETE'])
@admin_required
def delete_module(module_id):
    try:
        module = CourseModule.query.get(module_id)
        if not module:
            return jsonify({'error': 'Module not found'}), 404

        course_id = module.course_id
        deleted_order = module.order_index

        db.session.delete(module)

        # reorder remaining modules
        CourseModule.query.filter(
            CourseModule.course_id == course_id,
            CourseModule.order_index > deleted_order
        ).update(
            {CourseModule.order_index: CourseModule.order_index - 1},
            synchronize_session=False
        )

        db.session.commit()

        return jsonify({'message': 'Module deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



# ====== See User Enrollnment, progress, completed of course (Read only) ==========
# admins should observe, not “learn on behalf of users”
# mutations here easily corrupt analytics

@education_admin_bp.route('/courses/<int:course_id>/enrollments', methods=['GET'])
@admin_required
def list_course_enrollments(course_id):
    course = Course.query.get(course_id)
    if not course:
        return jsonify({'error': 'Course not found'}), 404

    enrollments = (
        db.session.query(UserEnrollment, User)
        .join(User, UserEnrollment.user_id == User.id)
        .filter(UserEnrollment.course_id == course_id)
        .order_by(UserEnrollment.enrolled_at.desc())
        .all()
    )

    return jsonify({
        'courseId': course.id,
        'title': course.title,
        'enrollments': [
            {
                'userId': user.id,
                'email': user.email,
                'status': e.status,
                'progress': e.progress,
                'enrolledAt': e.enrolled_at,
                'lastActivityAt': e.last_activity_at
            }
            for e, user in enrollments
        ]
    })
