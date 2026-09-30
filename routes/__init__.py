# Routes package
from routes.auth import auth_bp
from routes.jobs import jobs_bp
from routes.seeker import seeker_bp
from routes.employer import employer_bp
from routes.admin import admin_bp
from routes.api import api_bp

__all__ = ['auth_bp', 'jobs_bp', 'seeker_bp', 'employer_bp', 'admin_bp', 'api_bp']
