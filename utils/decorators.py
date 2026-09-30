import os
import uuid
from functools import wraps
from flask import abort, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, logout_user
from werkzeug.utils import secure_filename


def role_required(*roles):
    """
    Decorator to restrict view access to specific user roles.
    Example: @role_required('admin') or @role_required('employer', 'admin')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if not current_user.is_active:
                logout_user()
                flash('Your account has been deactivated. Please contact support.', 'danger')
                return redirect(url_for('auth.login'))

            if current_user.role not in roles:
                # Forbidden: Render custom 403 error page with HTTP 403 status
                return render_template('403.html', message="You do not have permission to view this resource."), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def allowed_file(filename: str, allowed_extensions: set = None) -> bool:
    """Validate file extension against allowed set."""
    if allowed_extensions is None:
        allowed_extensions = current_app.config.get('ALLOWED_EXTENSIONS', {'pdf', 'doc', 'docx'})
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_resume_file(file_storage, user_id: int) -> str:
    """
    Safely save an uploaded resume with secure naming and uuid prefix.
    Returns the saved filename.
    """
    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    os.makedirs(upload_folder, exist_ok=True)

    original_filename = secure_filename(file_storage.filename)
    extension = original_filename.rsplit('.', 1)[1].lower() if '.' in original_filename else 'pdf'
    
    unique_name = f"resume_u{user_id}_{uuid.uuid4().hex[:10]}.{extension}"
    destination = os.path.join(upload_folder, unique_name)
    file_storage.save(destination)

    return unique_name
