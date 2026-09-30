from datetime import datetime, date
from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import current_user
from sqlalchemy import func
from models import db, Job, Application, Profile, User
from utils.decorators import role_required
from routes.jobs import POPULAR_CATEGORIES, INDIAN_LOCATIONS, JOB_TYPES, EXPERIENCE_LEVELS

employer_bp = Blueprint('employer', __name__, url_prefix='/employer')


@employer_bp.route('/dashboard')
@role_required('employer')
def dashboard():
    """Employer dashboard displaying key metrics and recent applications."""
    total_jobs = Job.query.filter_by(employer_id=current_user.id).count()
    active_jobs = Job.query.filter_by(employer_id=current_user.id, is_active=True).count()

    # Total applications across all jobs of this employer
    total_applications = (
        Application.query.join(Job)
        .filter(Job.employer_id == current_user.id)
        .count()
    )
    
    shortlisted_candidates = (
        Application.query.join(Job)
        .filter(Job.employer_id == current_user.id, Application.status == Application.STATUS_SHORTLISTED)
        .count()
    )

    # Recent applications received
    recent_applications = (
        Application.query.join(Job)
        .filter(Job.employer_id == current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(6)
        .all()
    )

    # Recent jobs posted
    recent_jobs = (
        Job.query.filter_by(employer_id=current_user.id)
        .order_by(Job.created_at.desc())
        .limit(4)
        .all()
    )

    stats = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'shortlisted': shortlisted_candidates
    }

    return render_template(
        'employer/dashboard.html',
        stats=stats,
        recent_applications=recent_applications,
        recent_jobs=recent_jobs
    )


@employer_bp.route('/profile', methods=['GET', 'POST'])
@role_required('employer')
def profile():
    """Manage company profile details."""
    user_profile = current_user.profile
    if not user_profile:
        user_profile = Profile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        company_website = request.form.get('company_website', '').strip()
        location = request.form.get('location', '').strip()
        phone = request.form.get('phone', '').strip()
        bio = request.form.get('bio', '').strip()

        if not company_name:
            flash("Company Name is required.", "danger")
            return render_template('employer/profile.html', profile=user_profile)

        user_profile.company_name = company_name
        user_profile.company_website = company_website
        user_profile.location = location
        user_profile.phone = phone
        user_profile.bio = bio
        
        # Keep user display name aligned with company name
        current_user.name = company_name

        db.session.commit()
        flash("Company profile updated successfully.", "success")
        return redirect(url_for('employer.profile'))

    return render_template('employer/profile.html', profile=user_profile)


@employer_bp.route('/jobs')
@role_required('employer')
def manage_jobs():
    """List and manage all jobs posted by the logged-in employer."""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '').strip()

    query = Job.query.filter_by(employer_id=current_user.id)
    if status_filter == 'active':
        query = query.filter_by(is_active=True)
    elif status_filter == 'inactive':
        query = query.filter_by(is_active=False)

    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=10, error_out=False)

    return render_template(
        'employer/jobs.html',
        pagination=pagination,
        jobs=pagination.items,
        status_filter=status_filter
    )


@employer_bp.route('/jobs/create', methods=['GET', 'POST'])
@role_required('employer')
def create_job():
    """Post a new job opening."""
    user_profile = current_user.profile
    default_company = user_profile.company_name if (user_profile and user_profile.company_name) else current_user.name

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip() or default_company
        category = request.form.get('category', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', 'Full Time').strip()
        experience_level = request.form.get('experience_level', 'Entry Level').strip()
        salary_min = request.form.get('salary_min', type=int)
        salary_max = request.form.get('salary_max', type=int)
        skills = request.form.get('skills', '').strip()
        deadline_str = request.form.get('deadline', '').strip()
        description = request.form.get('description', '').strip()

        # Validation
        errors = []
        if not title:
            errors.append("Job Title is required.")
        if not company:
            errors.append("Company Name is required.")
        if not category:
            errors.append("Category is required.")
        if not location:
            errors.append("Location is required.")
        if not description or len(description) < 20:
            errors.append("Job description must be at least 20 characters long.")

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid deadline date format.")

        if salary_min and salary_max and salary_min > salary_max:
            errors.append("Minimum salary cannot be greater than maximum salary.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'employer/create_job.html',
                categories=POPULAR_CATEGORIES,
                locations=INDIAN_LOCATIONS,
                job_types=JOB_TYPES,
                experience_levels=EXPERIENCE_LEVELS,
                form_data=request.form
            )

        job = Job(
            employer_id=current_user.id,
            title=title,
            company=company,
            category=category,
            location=location,
            job_type=job_type,
            experience_level=experience_level,
            salary_min=salary_min,
            salary_max=salary_max,
            skills=skills,
            deadline=deadline,
            description=description,
            is_active=True
        )
        db.session.add(job)
        db.session.commit()

        flash("Job posted successfully!", "success")
        return redirect(url_for('employer.manage_jobs'))

    return render_template(
        'employer/create_job.html',
        categories=POPULAR_CATEGORIES,
        locations=INDIAN_LOCATIONS,
        job_types=JOB_TYPES,
        experience_levels=EXPERIENCE_LEVELS,
        default_company=default_company,
        form_data={}
    )


@employer_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@role_required('employer')
def edit_job(job_id):
    """Edit an existing job posted by the employer."""
    job = Job.query.get_or_404(job_id)

    # Ownership check
    if job.employer_id != current_user.id and not current_user.is_admin:
        abort(403)

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        company = request.form.get('company', '').strip()
        category = request.form.get('category', '').strip()
        location = request.form.get('location', '').strip()
        job_type = request.form.get('job_type', '').strip()
        experience_level = request.form.get('experience_level', '').strip()
        salary_min = request.form.get('salary_min', type=int)
        salary_max = request.form.get('salary_max', type=int)
        skills = request.form.get('skills', '').strip()
        deadline_str = request.form.get('deadline', '').strip()
        description = request.form.get('description', '').strip()
        is_active = bool(request.form.get('is_active'))

        errors = []
        if not title:
            errors.append("Job Title is required.")
        if not company:
            errors.append("Company Name is required.")
        if not category:
            errors.append("Category is required.")
        if not location:
            errors.append("Location is required.")
        if not description or len(description) < 20:
            errors.append("Job description must be at least 20 characters long.")

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date()
            except ValueError:
                errors.append("Invalid deadline date format.")

        if salary_min and salary_max and salary_min > salary_max:
            errors.append("Minimum salary cannot exceed maximum salary.")

        if errors:
            for error in errors:
                flash(error, 'danger')
            return render_template(
                'employer/edit_job.html',
                job=job,
                categories=POPULAR_CATEGORIES,
                locations=INDIAN_LOCATIONS,
                job_types=JOB_TYPES,
                experience_levels=EXPERIENCE_LEVELS
            )

        job.title = title
        job.company = company
        job.category = category
        job.location = location
        job.job_type = job_type
        job.experience_level = experience_level
        job.salary_min = salary_min
        job.salary_max = salary_max
        job.skills = skills
        job.deadline = deadline
        job.description = description
        job.is_active = is_active

        db.session.commit()
        flash("Job updated successfully.", "success")
        return redirect(url_for('employer.manage_jobs'))

    return render_template(
        'employer/edit_job.html',
        job=job,
        categories=POPULAR_CATEGORIES,
        locations=INDIAN_LOCATIONS,
        job_types=JOB_TYPES,
        experience_levels=EXPERIENCE_LEVELS
    )


@employer_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@role_required('employer')
def delete_job(job_id):
    """Delete a posted job."""
    job = Job.query.get_or_404(job_id)

    if job.employer_id != current_user.id and not current_user.is_admin:
        abort(403)

    db.session.delete(job)
    db.session.commit()
    flash("Job deleted successfully.", "success")
    return redirect(url_for('employer.manage_jobs'))


@employer_bp.route('/jobs/<int:job_id>/toggle-status', methods=['POST'])
@role_required('employer')
def toggle_job_status(job_id):
    """Activate or deactivate a job listing."""
    job = Job.query.get_or_404(job_id)

    if job.employer_id != current_user.id and not current_user.is_admin:
        abort(403)

    job.is_active = not job.is_active
    db.session.commit()
    status_msg = "activated" if job.is_active else "deactivated"
    flash(f"Job '{job.title}' has been {status_msg}.", "info")
    return redirect(request.referrer or url_for('employer.manage_jobs'))


@employer_bp.route('/applicants')
@employer_bp.route('/jobs/<int:job_id>/applicants')
@role_required('employer')
def applicants(job_id=None):
    """View and manage candidate applications."""
    selected_job = None
    query = Application.query.join(Job).filter(Job.employer_id == current_user.id)

    if not job_id:
        job_id = request.args.get('job_id', type=int)

    if job_id:
        selected_job = Job.query.get_or_404(job_id)
        if selected_job.employer_id != current_user.id and not current_user.is_admin:
            abort(403)
        query = query.filter(Application.job_id == job_id)

    status_filter = request.args.get('status', '').strip()
    if status_filter and status_filter in Application.VALID_STATUSES:
        query = query.filter(Application.status == status_filter)

    applications_list = query.order_by(Application.applied_at.desc()).all()
    employer_jobs = Job.query.filter_by(employer_id=current_user.id).order_by(Job.title).all()

    return render_template(
        'employer/applicants.html',
        applications=applications_list,
        selected_job=selected_job,
        employer_jobs=employer_jobs,
        status_filter=status_filter,
        statuses=Application.VALID_STATUSES
    )


@employer_bp.route('/applications/<int:app_id>/status', methods=['POST'])
@role_required('employer')
def update_application_status(app_id):
    """Change the status of an applicant."""
    application = Application.query.get_or_404(app_id)

    # Verify ownership of job
    if application.job.employer_id != current_user.id and not current_user.is_admin:
        abort(403)

    new_status = request.form.get('status', '').strip()
    if new_status in Application.VALID_STATUSES:
        application.status = new_status
        db.session.commit()
        flash(f"Application for '{application.seeker.name}' updated to '{new_status}'.", "success")
    else:
        flash("Invalid status specified.", "danger")

    return redirect(request.referrer or url_for('employer.applicants'))
