from datetime import datetime
from decimal import Decimal
from models.education import Course, CoursePurchase, UserEnrollment
from models import db

class CourseManager:
    @staticmethod
    def check_purchase(user_id, course_id):
        """Checks if a user has purchased a specific course"""
        return CoursePurchase.query.filter_by(
            user_id=user_id, 
            course_id=course_id, 
            payment_status='completed'
        ).first() is not None

    @staticmethod
    def record_purchase(user_id, course_id, amount, gateway, transaction_id):
        """Records a successful course purchase and auto-enrolls the user"""
        
        # 1. IDEMPOTENCY CHECK: Prevent double purchase record
        existing = CoursePurchase.query.filter_by(
            user_id=user_id, 
            course_id=course_id, 
            payment_status='completed'
        ).first()
        
        if existing:
            return True, "Course already purchased"

        course = Course.query.get(course_id)
        if not course:
            return False, "Course not found"

        # 2. Record the purchase
        purchase = CoursePurchase(
            user_id=user_id,
            course_id=course_id,
            amount_paid=Decimal(str(amount)),
            gateway=gateway,
            transaction_id=transaction_id,
            payment_status='completed'
        )
        db.session.add(purchase)

        # 3. Auto-enroll the user if not already enrolled
        enrollment = UserEnrollment.query.filter_by(
            user_id=user_id, 
            course_id=course_id
        ).first()

        if not enrollment:
            enrollment = UserEnrollment(
                user_id=user_id,
                course_id=course_id,
                status='enrolled',
                progress=0
            )
            db.session.add(enrollment)
        elif enrollment.status == 'unenrolled':
            enrollment.status = 'enrolled'
            enrollment.progress = 0

        try:
            db.session.commit()
            return True, "Purchase confirmed and enrollment active"
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"
