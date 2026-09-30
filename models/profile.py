from datetime import datetime, timezone
from models import db


class Profile(db.Model):
    """Profile information for Job Seekers and Employers."""
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    
    # Common fields
    phone = db.Column(db.String(20))
    location = db.Column(db.String(100))
    bio = db.Column(db.Text)
    
    # Seeker specific fields
    skills = db.Column(db.Text)         # e.g., "Python, Flask, React, SQL"
    education = db.Column(db.Text)      # e.g., "B.Tech in Computer Science, IIT Bombay (2020-2024)"
    experience = db.Column(db.Text)     # e.g., "2 Years as Junior Backend Developer at ABC Corp"
    
    # Employer specific fields
    company_name = db.Column(db.String(150))
    company_website = db.Column(db.String(200))
    
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def skills_list(self) -> list:
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone': self.phone,
            'location': self.location,
            'bio': self.bio,
            'skills': self.skills,
            'skills_list': self.skills_list,
            'education': self.education,
            'experience': self.experience,
            'company_name': self.company_name,
            'company_website': self.company_website,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    def __repr__(self) -> str:
        return f"<Profile user_id={self.user_id}>"
