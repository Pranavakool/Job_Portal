from datetime import datetime, timezone
from models import db


class Application(db.Model):
    """Job application submitted by a seeker."""
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id', ondelete='CASCADE'), nullable=False, index=True)
    seeker_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    resume_filename = db.Column(db.String(255), nullable=False)
    cover_letter = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='Applied', nullable=False, index=True)
    
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Unique constraint so a seeker cannot apply to the same job twice
    __table_args__ = (
        db.UniqueConstraint('job_id', 'seeker_id', name='uq_job_seeker_application'),
    )

    # Valid statuses
    STATUS_APPLIED = 'Applied'
    STATUS_UNDER_REVIEW = 'Under Review'
    STATUS_SHORTLISTED = 'Shortlisted'
    STATUS_REJECTED = 'Rejected'
    STATUS_HIRED = 'Hired'
    
    VALID_STATUSES = [
        STATUS_APPLIED,
        STATUS_UNDER_REVIEW,
        STATUS_SHORTLISTED,
        STATUS_REJECTED,
        STATUS_HIRED
    ]

    @property
    def badge_class(self) -> str:
        """Bootstrap badge class based on status."""
        mapping = {
            'Applied': 'bg-primary',
            'Under Review': 'bg-info text-dark',
            'Shortlisted': 'bg-warning text-dark',
            'Rejected': 'bg-danger',
            'Hired': 'bg-success'
        }
        return mapping.get(self.status, 'bg-secondary')

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_title': self.job.title if self.job else None,
            'company': self.job.company if self.job else None,
            'seeker_id': self.seeker_id,
            'seeker_name': self.seeker.name if self.seeker else None,
            'seeker_email': self.seeker.email if self.seeker else None,
            'resume_filename': self.resume_filename,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Application {self.id}: Seeker {self.seeker_id} -> Job {self.job_id} ({self.status})>"
