import re
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from urllib.parse import urlparse
from models import db, User, Profile

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")


def is_safe_url(target):
    """Ensure redirect URL is internal to prevent open redirect vulnerabilities."""
    ref_url = urlparse(request.host_url)
    test_url = urlparse(target)
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new Job Seeker or Employer."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_employer:
            return redirect(url_for('employer.dashboard'))
        return redirect(url_for('seeker.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        role = request.form.get('role', 'seeker').strip().lower()

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append("Full Name is required (minimum 2 characters).")
        if not email or not EMAIL_REGEX.match(email):
            errors.append("Please provide a valid email address.")
        if not password or len(password) < 6:
            errors.append("Password must be at least 6 characters long.")
        if password != confirm_password:
            errors.append("Passwords do not match.")
        
        # Strict role security check: public registration must NEVER allow 'admin'
        if role not in ('seeker', 'employer'):
            errors.append("Invalid account type selected. Only Job Seeker or Employer registration is allowed.")

        # Check existing user
        if not errors:
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                errors.append("An account with this email already exists. Please log in.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template('auth/register.html', name=name, email=email, role=role)

        # Create user and profile
        new_user = User(
            name=name,
            email=email,
            role=role,
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()  # Get new_user.id

        # Associated profile
        new_profile = Profile(
            user_id=new_user.id,
            company_name=name if role == 'employer' else None
        )
        db.session.add(new_profile)
        db.session.commit()

        flash("Registration successful! You can now log in with your credentials.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', role=request.args.get('role', 'seeker'))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Log in existing users."""
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif current_user.is_employer:
            return redirect(url_for('employer.dashboard'))
        return redirect(url_for('seeker.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        if not email or not password:
            flash("Please enter both email and password.", "danger")
            return render_template('auth/login.html', email=email)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            flash("Invalid email or password. Please try again.", "danger")
            return render_template('auth/login.html', email=email)

        # Check account activation status
        if not user.is_active:
            flash("Your account has been deactivated. Please contact support or an administrator.", "danger")
            return render_template('auth/login.html', email=email)

        login_user(user, remember=remember)
        flash(f"Welcome back, {user.name}!", "success")

        next_page = request.args.get('next')
        if next_page and is_safe_url(next_page):
            return redirect(next_page)

        # Default role-based landing page
        if user.is_admin:
            return redirect(url_for('admin.dashboard'))
        elif user.is_employer:
            return redirect(url_for('employer.dashboard'))
        else:
            return redirect(url_for('seeker.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Log out current user."""
    logout_user()
    flash("You have been successfully logged out.", "info")
    return redirect(url_for('jobs.index'))
