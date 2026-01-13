"""
Education Models (Courses, Quizzes, Webinars)
PeartoFinance Backend
"""
from datetime import datetime
from .base import db


class Instructor(db.Model):
    """Course instructors"""
    __tablename__ = 'instructors'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    bio = db.Column(db.Text)
    avatar_url = db.Column(db.Text)
    expertise = db.Column(db.Text)
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    students_taught = db.Column(db.Integer, default=0)
    courses_count = db.Column(db.Integer, default=0)
    social_links = db.Column(db.JSON)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'bio': self.bio,
            'avatarUrl': self.avatar_url,
            'expertise': self.expertise,
            'rating': float(self.rating) if self.rating else None,
            'coursesCount': self.courses_count
        }


class Course(db.Model):
    """Educational courses"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255))
    description = db.Column(db.Text)
    long_description = db.Column(db.Text)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    category = db.Column(db.String(100))
    level = db.Column(db.Enum('Beginner', 'Intermediate', 'Advanced'), default='Beginner')
    duration_hours = db.Column(db.Integer)
    duration_weeks = db.Column(db.Integer)
    price = db.Column(db.Numeric(10, 2))
    discount_price = db.Column(db.Numeric(10, 2))
    thumbnail_url = db.Column(db.Text)
    video_url = db.Column(db.Text)
    is_published = db.Column(db.Boolean, default=False)
    is_free = db.Column(db.Boolean, default=False)
    enrollment_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Numeric(2, 1), default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    requirements = db.Column(db.JSON)
    what_you_learn = db.Column(db.JSON)
    country_code = db.Column(db.String(10))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'durationHours': self.duration_hours,
            'price': float(self.price) if self.price else None,
            'thumbnailUrl': self.thumbnail_url,
            'isPublished': self.is_published,
            'isFree': self.is_free,
            'enrollmentCount': self.enrollment_count,
            'rating': float(self.rating) if self.rating else None
        }


class CourseModule(db.Model):
    """Course modules/sections"""
    __tablename__ = 'course_modules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    duration_minutes = db.Column(db.Integer)
    video_url = db.Column(db.Text)
    content = db.Column(db.Text)
    is_free = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Quiz(db.Model):
    """Quizzes"""
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'))
    time_limit_minutes = db.Column(db.Integer)
    passing_score = db.Column(db.Integer, default=70)
    max_attempts = db.Column(db.Integer, default=3)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class QuizQuestion(db.Model):
    """Quiz questions"""
    __tablename__ = 'quiz_questions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.Enum('multiple_choice', 'true_false', 'short_answer'), default='multiple_choice')
    options = db.Column(db.JSON)
    correct_answer = db.Column(db.Text)
    explanation = db.Column(db.Text)
    points = db.Column(db.Integer, default=1)
    order_index = db.Column(db.Integer, default=0)


class QuizAnswer(db.Model):
    """User quiz answers"""
    __tablename__ = 'quiz_answers'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('quiz_questions.id'), nullable=False)
    answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    points_earned = db.Column(db.Integer, default=0)


class QuizAttempt(db.Model):
    """Quiz attempts by users"""
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    score = db.Column(db.Integer)
    total_points = db.Column(db.Integer)
    passed = db.Column(db.Boolean)
    time_taken_seconds = db.Column(db.Integer)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)


class Webinar(db.Model):
    """Webinars/live sessions"""
    __tablename__ = 'webinars'
    
    id = db.Column(db.String(255), primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    host_id = db.Column(db.Integer, db.ForeignKey('instructors.id'))
    scheduled_at = db.Column(db.DateTime)
    duration_minutes = db.Column(db.Integer)
    max_attendees = db.Column(db.Integer)
    meeting_url = db.Column(db.Text)
    recording_url = db.Column(db.Text)
    status = db.Column(db.Enum('scheduled', 'live', 'completed', 'cancelled'), default='scheduled')
    is_free = db.Column(db.Boolean, default=False)
    price = db.Column(db.Numeric(10, 2))
    thumbnail_url = db.Column(db.Text)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class WebinarAttendance(db.Model):
    """Webinar attendance records"""
    __tablename__ = 'webinar_attendance'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    webinar_id = db.Column(db.String(255), db.ForeignKey('webinars.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)
    attended = db.Column(db.Boolean, default=False)
    join_time = db.Column(db.DateTime)
    leave_time = db.Column(db.DateTime)


class HelpCategory(db.Model):
    """Help article categories"""
    __tablename__ = 'help_categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100))
    icon = db.Column(db.String(50))
    description = db.Column(db.Text)
    order_index = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10), default='US')


class HelpArticle(db.Model):
    """Help center articles"""
    __tablename__ = 'help_articles'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255))
    content = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('help_categories.id'))
    is_featured = db.Column(db.Boolean, default=False)
    view_count = db.Column(db.Integer, default=0)
    helpful_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    country_code = db.Column(db.String(10), default='US')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserEnrollment(db.Model):
    """User course enrollments with progress tracking"""
    __tablename__ = 'user_enrollments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    current_module_id = db.Column(db.Integer, db.ForeignKey('course_modules.id'))
    status = db.Column(db.Enum('enrolled', 'in_progress', 'completed', 'paused'), default='enrolled')
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'userId': self.user_id,
            'courseId': self.course_id,
            'progress': self.progress,
            'currentModuleId': self.current_module_id,
            'status': self.status,
            'enrolledAt': self.enrolled_at.isoformat() if self.enrolled_at else None,
            'lastActivityAt': self.last_activity_at.isoformat() if self.last_activity_at else None,
            'completedAt': self.completed_at.isoformat() if self.completed_at else None
        }
