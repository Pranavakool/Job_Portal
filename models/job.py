from datetime import datetime, timezone
from models import db


class Job(db.Model):
    """Job vacancy posting by employers."""
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    
    title = db.Column(db.String(150), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    company = db.Column(db.String(150), nullable=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    location = db.Column(db.String(100), nullable=False, index=True)
    
    salary_min = db.Column(db.Integer, nullable=True)
    salary_max = db.Column(db.Integer, nullable=True)
    
    job_type = db.Column(db.String(50), nullable=False, default='Full Time', index=True)
    experience_level = db.Column(db.String(50), nullable=False, default='Entry Level', index=True)
    
    skills = db.Column(db.Text, nullable=True)  # Comma separated
    deadline = db.Column(db.Date, nullable=True)
    
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationship to applications
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')

    @property
    def skills_list(self) -> list:
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    @property
    def salary_display(self) -> str:
        """Formatted salary range string (e.g. ₹6,00,000 - ₹12,00,000 / yr)."""
        if self.salary_min and self.salary_max:
            return f"₹{self.salary_min:,} - ₹{self.salary_max:,} / yr"
        elif self.salary_min:
            return f"From ₹{self.salary_min:,} / yr"
        elif self.salary_max:
            return f"Up to ₹{self.salary_max:,} / yr"
        return "Competitive / Negotiable"

    @property
    def application_count(self) -> int:
        return len(self.applications)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'title': self.title,
            'company': self.company,
            'category': self.category,
            'location': self.location,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'salary_display': self.salary_display,
            'job_type': self.job_type,
            'experience_level': self.experience_level,
            'skills': self.skills,
            'skills_list': self.skills_list,
            'description': self.description,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'application_count': self.application_count
        }

    def __repr__(self) -> str:
        return f"<Job {self.id}: {self.title} at {self.company}>"
