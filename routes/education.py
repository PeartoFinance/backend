"""
Education API Routes (Public + Authenticated)
Courses, Instructors, and Learning resources
"""
"""
User Education Routes (Learning Flow)

This file implements the complete *user-side* learning lifecycle:
- enroll in course
- view enrolled courses
- view a specific enrolled course
- complete modules
- track progress
- auto-complete course at 100%

Design principles:
- Action-based APIs (no direct status mutation from frontend)
- Backend-owned state transitions
- Enrollment-scoped access (users can only act on courses they are enrolled in)
- Minimal progress tracking (single progress field on enrollment)

IMPORTANT:
- Do NOT add endpoints that directly set enrollment.status
- Course completion is derived from module completion only
- Seed data may cause module/course mismatch; logic assumes real user flow
"""
# Enrollment check is intentionally done via course_id derived from the module.
# This prevents users from completing modules belonging to courses
# they are not enrolled in (do NOT relax this check).



from flask import Blueprint, jsonify, request, g
from models import Course, Instructor, CourseModule, UserEnrollment
from models.base import db
from routes.decorators import auth_required

education_bp = Blueprint("education", __name__)


def is_course_visible_to_user(course, user_country):
    if course.country_code == "GLOBAL":
        return True
    return course.country_code == user_country


@education_bp.route("/courses", methods=["GET"])
def get_courses():
    """Get all published courses with optional filtering"""
    try:
        category = request.args.get("category")
        level = request.args.get("level")
        is_free = request.args.get("free")
        search = request.args.get("search")

        # Determine country filter: GLOBAL courses visible to all, plus country-specific
        header_country = request.headers.get("X-User-Country")
        if header_country is None:
            # No header -> show US + GLOBAL
            country_filter = Course.country_code.in_(["US", "GLOBAL"])
        else:
            hc = header_country.strip().upper()
            if hc == "GLOBAL":
                country_filter = (Course.country_code == "GLOBAL")
            else:
                # Show country-specific + GLOBAL courses
                country_filter = Course.country_code.in_([hc, "GLOBAL"])

        query = Course.query.filter(Course.is_published == True, country_filter)

        if category:
            query = query.filter(Course.category == category)
        if level:
            query = query.filter(Course.level == level)
        if is_free == "true":
            query = query.filter(Course.is_free == True)
        if search:
            query = query.filter(Course.title.ilike(f"%{search}%"))

        courses = query.order_by(Course.created_at.desc()).all()

        return jsonify(
            {
                "courses": [
                    {
                        "id": c.id,
                        "title": c.title,
                        "slug": c.slug,
                        "description": c.description,
                        "category": c.category,
                        "countryCode": c.country_code,
                        "level": c.level,
                        "durationHours": c.duration_hours,
                        "durationWeeks": c.duration_weeks,
                        "price": float(c.price) if c.price else 0,
                        "discountPrice": (
                            float(c.discount_price) if c.discount_price else None
                        ),
                        "thumbnailUrl": c.thumbnail_url,
                        "isFree": c.is_free,
                        "enrollmentCount": c.enrollment_count or 0,
                        "rating": float(c.rating) if c.rating else 0,
                        "ratingCount": c.rating_count or 0,
                        "instructorId": c.instructor_id,
                    }
                    for c in courses
                ],
                "total": len(courses),
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@education_bp.route("/courses/<slug>", methods=["GET"])
def get_course(slug):
    """Get single course by slug with modules"""
    try:
        header_country = request.headers.get("X-User-Country")
        if header_country is None:
            country_filter = Course.country_code.in_(["US", "GLOBAL"])
        else:
            hc = header_country.strip().upper()
            if hc == "GLOBAL":
                country_filter = (Course.country_code == "GLOBAL")
            else:
                country_filter = Course.country_code.in_([hc, "GLOBAL"])

        course = Course.query.filter(
            Course.slug == slug, Course.is_published == True, country_filter
        ).first()

        if not course:
            return jsonify({"error": "Course not found"}), 404

        # Get modules
        modules = (
            CourseModule.query.filter(CourseModule.course_id == course.id)
            .order_by(CourseModule.order_index)
            .all()
        )

        # Get instructor
        instructor = None
        if course.instructor_id:
            inst = Instructor.query.get(course.instructor_id)
            if inst:
                instructor = {
                    "id": inst.id,
                    "name": inst.name,
                    "title": inst.title,
                    "bio": inst.bio,
                    "avatarUrl": inst.avatar_url,
                    "rating": float(inst.rating) if inst.rating else None,
                }

        return jsonify(
            {
                "id": course.id,
                "title": course.title,
                "slug": course.slug,
                "description": course.description,
                "longDescription": course.long_description,
                "category": course.category,
                "level": course.level,
                "durationHours": course.duration_hours,
                "durationWeeks": course.duration_weeks,
                "price": float(course.price) if course.price else 0,
                "discountPrice": (
                    float(course.discount_price) if course.discount_price else None
                ),
                "thumbnailUrl": course.thumbnail_url,
                "videoUrl": course.video_url,
                "isFree": course.is_free,
                "enrollmentCount": course.enrollment_count or 0,
                "rating": float(course.rating) if course.rating else 0,
                "ratingCount": course.rating_count or 0,
                "requirements": course.requirements or [],
                "whatYouLearn": course.what_you_learn or [],
                "instructor": instructor,
                "modules": [
                    {
                        "id": m.id,
                        "title": m.title,
                        "description": m.description,
                        "durationMinutes": m.duration_minutes,
                        "isFree": m.is_free,
                    }
                    for m in modules
                ],
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@education_bp.route("/instructors", methods=["GET"])
def get_instructors():
    """Get all active instructors"""
    try:
        # Apply country scoping for instructors (include GLOBAL)
        header_country = request.headers.get("X-User-Country")
        if header_country is None:
            instructor_filter = Instructor.country_code.in_(["US", "GLOBAL"])
        else:
            hc = header_country.strip().upper()
            if hc == "GLOBAL":
                instructor_filter = (Instructor.country_code == "GLOBAL")
            else:
                instructor_filter = Instructor.country_code.in_([hc, "GLOBAL"])

        instructors = (
            Instructor.query.filter(Instructor.is_active == True, instructor_filter)
            .order_by(Instructor.courses_count.desc())
            .all()
        )

        return jsonify(
            {
                "instructors": [
                    {
                        "id": i.id,
                        "name": i.name,
                        "title": i.title,
                        "bio": i.bio,
                        "avatarUrl": i.avatar_url,
                        "expertise": i.expertise,
                        "rating": float(i.rating) if i.rating else 0,
                        "studentsTaught": i.students_taught or 0,
                        "coursesCount": i.courses_count or 0,
                    }
                    for i in instructors
                ]
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@education_bp.route("/categories", methods=["GET"])
def get_categories():
    """Get unique course categories"""
    try:
        header_country = request.headers.get("X-User-Country")
        if header_country is None:
            cat_filter = Course.country_code.in_(["US", "GLOBAL"])
        else:
            hc = header_country.strip().upper()
            if hc == "GLOBAL":
                cat_filter = (Course.country_code == "GLOBAL")
            else:
                cat_filter = Course.country_code.in_([hc, "GLOBAL"])

        categories = (
            db.session.query(Course.category)
            .filter(Course.is_published == True, Course.category != None, cat_filter)
            .distinct()
            .all()
        )

        return jsonify({"categories": [c[0] for c in categories if c[0]]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@education_bp.route("/my-courses", methods=["GET"])
@auth_required
def get_my_courses():
    """Get authenticated user's enrolled courses with progress"""
    try:
        user_id = g.user_id

        # Get user's enrollments with course details
        enrollments = (
            db.session.query(UserEnrollment, Course, Instructor, CourseModule)
            .join(Course, UserEnrollment.course_id == Course.id)
            .outerjoin(Instructor, Course.instructor_id == Instructor.id)
            .outerjoin(
                CourseModule, UserEnrollment.current_module_id == CourseModule.id
            )
            .filter(
                UserEnrollment.user_id == user_id,
                UserEnrollment.status.in_(["enrolled", "in_progress", "paused"]),
            )
            .order_by(UserEnrollment.last_activity_at.desc())
            .all()
        )

        courses = []

        for enrollment, course, instructor, current_module in enrollments:
            courses.append(
                {
                    "enrollmentId": enrollment.id,
                    "courseId": course.id,
                    "title": course.title,
                    "countryCode": course.country_code,
                    "slug": course.slug,
                    "thumbnailUrl": course.thumbnail_url,
                    "category": course.category,
                    "instructor": {
                        "id": instructor.id if instructor else None,
                        "name": instructor.name if instructor else "Unknown",
                        "title": instructor.title if instructor else None,
                    },
                    "level": course.level,
                    "progress": enrollment.progress or 0,
                    "status": enrollment.status,
                    "currentModule": (
                        {"id": current_module.id, "title": current_module.title}
                        if current_module
                        else None
                    ),
                    "enrolledAt": (
                        enrollment.enrolled_at.isoformat()
                        if enrollment.enrolled_at
                        else None
                    ),
                    "lastActivityAt": (
                        enrollment.last_activity_at.isoformat()
                        if enrollment.last_activity_at
                        else None
                    ),
                }
            )
            print(
                "COURSE ID:", course.id, "RAW country_code:", repr(course.country_code)
            )

        return jsonify({"courses": courses, "total": len(courses)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# user enroll in course
@education_bp.route("/courses/<int:course_id>/enroll", methods=["POST"])
@auth_required
def enroll_in_course(course_id):
    try:
        user_id = g.user_id
        user_country = g.user_country

        # 1. Course must exist & be published
        course = Course.query.filter(
            Course.id == course_id, Course.is_published == True
        ).first()

        if not course:
            return jsonify({"error": "Course not found or not available"}), 404

        # 2. Country visibility
        if course.country_code not in ("GLOBAL", user_country):
            return jsonify({"error": "Course not available in your region"}), 403

        # 3. Check existing enrollment (NO status filter)
        enrollment = UserEnrollment.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()

        # Case A: Already actively enrolled
        if enrollment and enrollment.status in ["enrolled", "in_progress", "paused"]:
            return jsonify({"error": "Already enrolled"}), 409

        # Case B: Re-enroll after unenroll
        if enrollment and enrollment.status == "unenrolled":
            enrollment.status = "enrolled"
            enrollment.progress = 0
            enrollment.enrolled_at = db.func.now()
            enrollment.last_activity_at = db.func.now()

            db.session.commit()

            return (
                jsonify(
                    {
                        "message": "Re-enrolled successfully",
                        "enrollmentId": enrollment.id,
                        "courseId": course_id,
                        "status": enrollment.status,
                    }
                ),
                200,
            )

        # Case C: First-time enrollment
        enrollment = UserEnrollment(
            user_id=user_id, course_id=course_id, status="enrolled", progress=0
        )

        db.session.add(enrollment)
        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Enrolled successfully",
                    "enrollmentId": enrollment.id,
                    "courseId": course_id,
                    "status": enrollment.status,
                }
            ),
            201,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Enrollment failed"}), 500


# unenroll from enrolled course
@education_bp.route("/courses/<int:course_id>/unenroll", methods=["POST"])
@auth_required
def unenroll_course(course_id):
    try:
        user_id = g.user_id

        enrollment = UserEnrollment.query.filter_by(
            user_id=user_id, course_id=course_id
        ).first()

        if enrollment.status == "completed":
            return jsonify({"error": "Completed course cannot be unenrolled"}), 400

        if enrollment.status == "unenrolled":
            return (
                jsonify({"message": "Already unenrolled", "status": enrollment.status}),
                200,
            )

        if not enrollment:
            return jsonify({"error": "Enrollment not found"}), 404

        if enrollment.status != "enrolled":
            return (
                jsonify(
                    {
                        "error": f"Cannot unenroll from course with status {enrollment.status}"
                    }
                ),
                400,
            )

        # ✅ Soft unenroll
        enrollment.status = "unenrolled"
        enrollment.last_activity_at = db.func.now()

        db.session.commit()

        return (
            jsonify(
                {
                    "message": "Unenrolled successfully",
                    "courseId": course_id,
                    "status": enrollment.status,
                }
            ),
            200,
        )

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to unenroll"}), 500


# track course modules completion
@education_bp.route("/modules/<int:module_id>/complete", methods=["POST"])
@auth_required
def complete_module(module_id):
    try:
        user_id = g.user_id

        # 1. Get module
        module = CourseModule.query.get(module_id)
        if not module:
            return jsonify({"error": "Module not found"}), 404
        
        print(f"DEBUG: complete_module - user_id: {user_id}, module_id: {module_id}, course_id: {module.course_id}")
        
        # 2. Get enrollment for this course
        enrollment = db.session.query(UserEnrollment).filter(
            UserEnrollment.user_id == user_id,
            UserEnrollment.course_id == module.course_id
        ).first()

        if not enrollment:
            # Enhanced Debugging
            all_user_enrollments = UserEnrollment.query.filter_by(user_id=user_id).all()
            enrolled_course_ids = [e.course_id for e in all_user_enrollments]
            
            return jsonify({
                "error": "You are not enrolled in this course",
                "debug_info": {
                    "requested_module_id": module_id,
                    "module_course_id": module.course_id,
                    "your_enrolled_courses": enrolled_course_ids
                }
            }), 403

        # 3. Check enrollment status
        if enrollment.status not in ["enrolled", "in_progress"]:
            return jsonify({
                "error": f"Cannot complete module when course is {enrollment.status}"
            }), 400

        # 4. Get total modules count
        total_modules = CourseModule.query.filter_by(
            course_id=module.course_id
        ).count()

        if total_modules == 0:
            return jsonify({"error": "Course has no modules"}), 400

        # 5. Calculate progress increment
        increment = 100 / total_modules
        new_progress = min(100, (enrollment.progress or 0) + increment)

        # 6. Update enrollment
        enrollment.progress = int(new_progress)
        enrollment.current_module_id = module.id
        enrollment.last_activity_at = db.func.now()

        # First module completion → in_progress
        if enrollment.status == "enrolled":
            enrollment.status = "in_progress"

        # Last module → completed
        if enrollment.progress >= 100:
            enrollment.status = "completed"
            enrollment.progress = 100

        db.session.commit()

        return jsonify({
            "message": "Module completed",
            "courseId": module.course_id,
            "moduleId": module.id,
            "progress": enrollment.progress,
            "status": enrollment.status
        }), 200

    except Exception:
        db.session.rollback()
        return jsonify({"error": "Failed to complete module"}), 500


#  get my-course detail by course_id
@education_bp.route("/my-courses/<int:course_id>", methods=["GET"])
@auth_required
def get_my_course(course_id):
    try:
        user_id = g.user_id

        enrollment = (
            db.session.query(UserEnrollment)
            .filter(
                UserEnrollment.user_id == user_id,
                UserEnrollment.course_id == course_id,
                UserEnrollment.status != "unenrolled"
            )
            .first()
        )

        if not enrollment:
            return jsonify({"error": "Course not found"}), 404

        course = Course.query.get(course_id)
        if not course:
            return jsonify({"error": "Course not found"}), 404

        modules = (
            CourseModule.query
            .filter_by(course_id=course.id)
            .order_by(CourseModule.order_index)
            .all()
        )

        # Fetch instructor separately
        instructor = None
        if course.instructor_id:
            instructor = Instructor.query.get(course.instructor_id)

        return jsonify({
            "course": {
                "id": course.id,
                "title": course.title,
                "slug": course.slug,
                "description": course.description,
                "level": course.level,
                "thumbnailUrl": course.thumbnail_url,
                "instructor": {
                    "id": instructor.id,
                    "name": instructor.name,
                    "title": instructor.title
                } if instructor else None,
                "modules": [
                    {
                        "id": m.id,
                        "title": m.title,
                        "durationMinutes": m.duration_minutes,
                        "isFree": m.is_free
                    }
                    for m in modules
                ]
            },
            "enrollment": {
                "status": enrollment.status,
                "progress": enrollment.progress,
                "currentModuleId": enrollment.current_module_id
            }
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

