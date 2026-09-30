from flask import Blueprint, render_template, request, flash, redirect, url_for, abort, current_app
from flask_login import current_user
from sqlalchemy import or_, func
from models import db, User, Job, Application, Profile
from utils.decorators import role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard')
@role_required('admin')
def dashboard():
    """Admin analytics and management overview."""
    total_users = User.query.count()
    total_seekers = User.query.filter_by(role='seeker').count()
    total_employers = User.query.filter_by(role='employer').count()
    total_admins = User.query.filter_by(role='admin').count()
    
    total_jobs = Job.query.count()
    active_jobs = Job.query.filter_by(is_active=True).count()
    inactive_jobs = total_jobs - active_jobs

    total_applications = Application.query.count()
    
    # Status breakdown
    status_counts = dict(
        db.session.query(Application.status, func.count(Application.id))
        .group_by(Application.status)
        .all()
    )

    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    recent_applications = Application.query.order_by(Application.applied_at.desc()).limit(5).all()

    stats = {
        'total_users': total_users,
        'total_seekers': total_seekers,
        'total_employers': total_employers,
        'total_admins': total_admins,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'status_counts': status_counts
    }

    return render_template(
        'admin/dashboard.html',
        stats=stats,
        recent_users=recent_users,
        recent_jobs=recent_jobs,
        recent_applications=recent_applications
    )


@admin_bp.route('/users')
@role_required('admin')
def users():
    """Manage all registered users (Seekers, Employers, Admins)."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    role_filter = request.args.get('role', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = User.query

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    if role_filter:
        query = query.filter(User.role == role_filter)

    if status_filter == 'active':
        query = query.filter(User.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(User.is_active == False)

    query = query.order_by(User.created_at.desc())
    pagination = query.paginate(page=page, per_page=current_app.config.get('USERS_PER_PAGE', 15), error_out=False)

    return render_template(
        'admin/users.html',
        pagination=pagination,
        users=pagination.items,
        search=search,
        role_filter=role_filter,
        status_filter=status_filter
    )


@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_user_status(user_id):
    """Activate or deactivate a user account."""
    user = User.query.get_or_404(user_id)

    # Protect against self-deactivation
    if user.id == current_user.id:
        flash("You cannot deactivate your own active admin account.", "danger")
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    db.session.commit()
    
    state = "activated" if user.is_active else "deactivated"
    flash(f"User account '{user.email}' has been {state}.", "info")
    return redirect(request.referrer or url_for('admin.users'))


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@role_required('admin')
def delete_user(user_id):
    """Delete a user account and associated records."""
    user = User.query.get_or_404(user_id)

    # Protect against self-deletion
    if user.id == current_user.id:
        flash("You cannot delete your own admin account.", "danger")
        return redirect(url_for('admin.users'))

    email = user.email
    db.session.delete(user)
    db.session.commit()

    flash(f"User '{email}' and all associated records have been permanently removed.", "success")
    return redirect(url_for('admin.users'))


@admin_bp.route('/jobs')
@role_required('admin')
def jobs():
    """Manage all job listings."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    category_filter = request.args.get('category', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Job.query

    if search:
        query = query.filter(
            or_(
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%"),
                Job.location.ilike(f"%{search}%")
            )
        )

    if category_filter:
        query = query.filter(Job.category == category_filter)

    if status_filter == 'active':
        query = query.filter(Job.is_active == True)
    elif status_filter == 'inactive':
        query = query.filter(Job.is_active == False)

    query = query.order_by(Job.created_at.desc())
    pagination = query.paginate(page=page, per_page=15, error_out=False)

    categories = [c[0] for c in db.session.query(Job.category).distinct().all()]

    return render_template(
        'admin/jobs.html',
        pagination=pagination,
        jobs=pagination.items,
        search=search,
        category_filter=category_filter,
        status_filter=status_filter,
        categories=categories
    )


@admin_bp.route('/jobs/<int:job_id>/toggle-status', methods=['POST'])
@role_required('admin')
def toggle_job_status(job_id):
    """Activate or deactivate a job listing from the admin console."""
    job = Job.query.get_or_404(job_id)
    job.is_active = not job.is_active
    db.session.commit()
    
    state = "activated" if job.is_active else "deactivated"
    flash(f"Job '{job.title}' by {job.company} has been {state}.", "info")
    return redirect(request.referrer or url_for('admin.jobs'))


@admin_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@role_required('admin')
def delete_job(job_id):
    """Remove inappropriate or spam job listing."""
    job = Job.query.get_or_404(job_id)
    title = job.title
    db.session.delete(job)
    db.session.commit()

    flash(f"Job listing '{title}' has been removed.", "success")
    return redirect(url_for('admin.jobs'))


@admin_bp.route('/applications')
@role_required('admin')
def applications():
    """View and filter all job applications across the entire platform."""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()

    query = Application.query.join(User, Application.seeker_id == User.id).join(Job, Application.job_id == Job.id)

    if search:
        query = query.filter(
            or_(
                User.name.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                Job.title.ilike(f"%{search}%"),
                Job.company.ilike(f"%{search}%")
            )
        )

    if status_filter and status_filter in Application.VALID_STATUSES:
        query = query.filter(Application.status == status_filter)

    query = query.order_by(Application.applied_at.desc())
    pagination = query.paginate(page=page, per_page=current_app.config.get('APPLICATIONS_PER_PAGE', 10), error_out=False)

    return render_template(
        'admin/applications.html',
        pagination=pagination,
        applications=pagination.items,
        search=search,
        status_filter=status_filter,
        statuses=Application.VALID_STATUSES
    )
