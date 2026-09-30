import os
from flask import Blueprint, render_template, request, flash, redirect, url_for, send_from_directory, current_app, abort
from flask_login import current_user, login_required
from models import db, User, Profile, Job, Application
from utils.decorators import role_required

seeker_bp = Blueprint('seeker', __name__, url_prefix='/seeker')


@seeker_bp.route('/dashboard')
@role_required('seeker')
def dashboard():
    """Job Seeker dashboard with statistics and recent activity."""
    # Stats
    total_apps = Application.query.filter_by(seeker_id=current_user.id).count()
    under_review = Application.query.filter_by(seeker_id=current_user.id, status=Application.STATUS_UNDER_REVIEW).count()
    shortlisted = Application.query.filter_by(seeker_id=current_user.id, status=Application.STATUS_SHORTLISTED).count()
    rejected = Application.query.filter_by(seeker_id=current_user.id, status=Application.STATUS_REJECTED).count()
    hired = Application.query.filter_by(seeker_id=current_user.id, status=Application.STATUS_HIRED).count()

    # Recent applications
    recent_apps = (
        Application.query.filter_by(seeker_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    # Recommended jobs
    seeker_profile = current_user.profile
    recommended_jobs = []
    if seeker_profile and seeker_profile.skills_list:
        first_skill = seeker_profile.skills_list[0]
        recommended_jobs = (
            Job.query.filter(
                Job.is_active == True,
                Job.skills.ilike(f"%{first_skill}%")
            )
            .order_by(Job.created_at.desc())
            .limit(4)
            .all()
        )
    if not recommended_jobs:
        recommended_jobs = (
            Job.query.filter_by(is_active=True)
            .order_by(Job.created_at.desc())
            .limit(4)
            .all()
        )

    stats = {
        'total': total_apps,
        'under_review': under_review,
        'shortlisted': shortlisted,
        'rejected': rejected,
        'hired': hired
    }

    return render_template(
        'seeker/dashboard.html',
        stats=stats,
        recent_apps=recent_apps,
        recommended_jobs=recommended_jobs
    )


@seeker_bp.route('/applications')
@role_required('seeker')
def applications():
    """View and filter all submitted applications."""
    status_filter = request.args.get('status', '').strip()
    page = request.args.get('page', 1, type=int)

    query = Application.query.filter_by(seeker_id=current_user.id)

    if status_filter and status_filter in Application.VALID_STATUSES:
        query = query.filter_by(status=status_filter)

    query = query.order_by(Application.applied_at.desc())
    pagination = query.paginate(page=page, per_page=current_app.config.get('APPLICATIONS_PER_PAGE', 10), error_out=False)

    return render_template(
        'seeker/applications.html',
        pagination=pagination,
        applications=pagination.items,
        current_status=status_filter,
        statuses=Application.VALID_STATUSES
    )


@seeker_bp.route('/profile', methods=['GET', 'POST'])
@role_required('seeker')
def profile():
    """View and update Job Seeker profile."""
    user_profile = current_user.profile
    if not user_profile:
        user_profile = Profile(user_id=current_user.id)
        db.session.add(user_profile)
        db.session.commit()

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        phone = request.form.get('phone', '').strip()
        location = request.form.get('location', '').strip()
        bio = request.form.get('bio', '').strip()
        skills = request.form.get('skills', '').strip()
        education = request.form.get('education', '').strip()
        experience = request.form.get('experience', '').strip()

        if not name or len(name) < 2:
            flash("Full Name is required.", "danger")
            return render_template('seeker/profile.html', profile=user_profile)

        current_user.name = name
        user_profile.phone = phone
        user_profile.location = location
        user_profile.bio = bio
        user_profile.skills = skills
        user_profile.education = education
        user_profile.experience = experience

        db.session.commit()
        flash("Profile updated successfully.", "success")
        return redirect(url_for('seeker.profile'))

    return render_template('seeker/profile.html', profile=user_profile)


@seeker_bp.route('/resume/<filename>')
@login_required
def download_resume(filename):
    """
    Secure resume download route.
    Authorized for:
    - Seeker who submitted the resume
    - Employer whose job received the resume
    - Admins
    """
    app_record = Application.query.filter_by(resume_filename=filename).first_or_404()

    is_owner = (current_user.id == app_record.seeker_id)
    is_job_employer = (current_user.id == app_record.job.employer_id)
    is_admin = current_user.is_admin

    if not (is_owner or is_job_employer or is_admin):
        abort(403)

    upload_folder = current_app.config.get('UPLOAD_FOLDER')
    return send_from_directory(upload_folder, filename, as_attachment=True)
