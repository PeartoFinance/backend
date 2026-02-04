"""
Cron Job Model
Stores queued background jobs for sequential execution
"""
from datetime import datetime
from .base import db
import enum

class JobStatus(enum.Enum):
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'

class CronJob(db.Model):
    __tablename__ = 'cron_jobs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    job_name = db.Column(db.String(100), nullable=False)
    params = db.Column(db.JSON)  # Store params if needed
    status = db.Column(db.Enum(JobStatus), default=JobStatus.PENDING)
    result = db.Column(db.Text)
    error = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_name': self.job_name,
            'status': self.status.value,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
