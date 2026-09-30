from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Import models so they are registered with SQLAlchemy
from models.user import User
from models.profile import Profile
from models.job import Job
from models.application import Application

__all__ = ['db', 'User', 'Profile', 'Job', 'Application']
