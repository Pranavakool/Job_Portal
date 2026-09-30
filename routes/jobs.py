from datetime import date
from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user
from sqlalchemy import or_, and_, func
from models import db, Job, User, Application, Profile
from utils.decorators import role_required, allowed_file, save_resume_file
from services.external_api import ExternalJobService

jobs_bp = Blueprint('jobs', __name__)

POPULAR_CATEGORIES = [
    'IT & Software',
    'Finance & Banking',
    'Marketing & Sales',
    'Human Resources',
    'Design & Creative',
    'Engineering',
    'Healthcare',
    'Education',
    'Operations',
    'Customer Support'
]

INDIAN_LOCATIONS = [
    'Pune',
    'Mumbai',
    'Bengaluru',
    'Hyderabad',
    'Chennai',
    'Delhi NCR',
    'Noida',
    'Gurugram',
    'Ahmedabad',
    'Kolkata',
    'Remote'
]

JOB_TYPES = ['Full Time', 'Part Time', 'Internship', 'Contract', 'Remote']
EXPERIENCE_LEVELS = ['Entry Level', 'Mid Level', 'Senior Level', 'Lead / Manager', 'Executive']


@jobs_bp.route('/')
def index():
    """Modern, vibrant landing page."""
    # Aggregated platform statistics
    total_active_jobs = Job.query.filter_by(is_active=True).count()
    total_companies = db.session.query(func.count(func.distinct(Job.company))).filter(Job.is_active == True).scalar() or 0
    total_seekers = User.query.filter_by(role='seeker', is_active=True).count()
    total_applications = Application.query.count()

    # Latest 6 active jobs
    latest_jobs = (
        Job.query.filter_by(is_active=True)
        .order_by(Job.created_at.desc())
        .limit(6)
        .all()
    )

    # Categories with count of active jobs
    category_counts = (
        db.session.query(Job.category, func.count(Job.id))
        .filter(Job.is_active == True)
        .group_by(Job.category)
        .order_by(func.count(Job.id).desc())
        .limit(8)
        .all()
    )

    return render_template(
        'index.html',
        stats={
            'total_jobs': total_active_jobs,
            'total_companies': total_companies,
            'total_seekers': total_seekers,
            'total_applications': total_applications
        },
        latest_jobs=latest_jobs,
        category_counts=category_counts,
        popular_locations=INDIAN_LOCATIONS[:6]
    )


@jobs_bp.route('/jobs')
def list_jobs():
    """Browse, search, and filter jobs with pagination."""
    page = request.args.get('page', 1, type=int)
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    category = request.args.get('category', '').strip()
    job_type = request.args.get('job_type', '').strip()
    experience_level = request.args.get('experience_level', '').strip()
    company = request.args.get('company', '').strip()
    min_salary = request.args.get('min_salary', type=int)
    sort_by = request.args.get('sort_by', 'newest').strip()

    # Build database query dynamically
    query = Job.query.filter_by(is_active=True)

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(pattern),
                Job.description.ilike(pattern),
                Job.company.ilike(pattern),
                Job.skills.ilike(pattern)
            )
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    if category:
        query = query.filter(Job.category == category)

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if experience_level:
        query = query.filter(Job.experience_level == experience_level)

    if company:
        query = query.filter(Job.company.ilike(f"%{company}%"))

    if min_salary:
        query = query.filter(
            or_(
                Job.salary_min >= min_salary,
                Job.salary_max >= min_salary
            )
        )

    # Sorting
    if sort_by == 'salary_high':
        query = query.order_by(Job.salary_max.desc().nullslast(), Job.created_at.desc())
    elif sort_by == 'salary_low':
        query = query.order_by(Job.salary_min.asc().nullslast(), Job.created_at.desc())
    elif sort_by == 'oldest':
        query = query.order_by(Job.created_at.asc())
    else:  # newest
        query = query.order_by(Job.created_at.desc())

    per_page = current_app.config.get('JOBS_PER_PAGE', 9)
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Distinct categories and locations for filter dropdowns
    all_categories = (
        db.session.query(Job.category)
        .filter(Job.is_active == True)
        .distinct()
        .order_by(Job.category)
        .all()
    )
    all_categories = [c[0] for c in all_categories]

    # Optional external jobs if search keyword is provided
    external_jobs = []
    if keyword and page == 1:
        external_jobs = ExternalJobService.fetch_jobs(keyword=keyword, location=location, limit=3)

    return render_template(
        'jobs/jobs.html',
        pagination=pagination,
        jobs=pagination.items,
        keyword=keyword,
        location=location,
        category=category,
        job_type=job_type,
        experience_level=experience_level,
        company=company,
        min_salary=min_salary,
        sort_by=sort_by,
        all_categories=all_categories,
        all_locations=INDIAN_LOCATIONS,
        all_job_types=JOB_TYPES,
        all_exp_levels=EXPERIENCE_LEVELS,
        external_jobs=external_jobs
    )


@jobs_bp.route('/jobs/<int:job_id>')
def job_detail(job_id):
    """View complete job listing details."""
    job = Job.query.get_or_404(job_id)

    # Check if job is inactive and viewer is not the owner or admin
    if not job.is_active:
        if not current_user.is_authenticated or (current_user.id != job.employer_id and not current_user.is_admin):
            flash("This job posting is no longer active.", "warning")
            return redirect(url_for('jobs.list_jobs'))

    # Check if current logged-in seeker has already applied
    existing_application = None
    if current_user.is_authenticated and current_user.is_seeker:
        existing_application = Application.query.filter_by(
            job_id=job.id,
            seeker_id=current_user.id
        ).first()

    # Similar jobs in the same category
    similar_jobs = (
        Job.query.filter(
            Job.category == job.category,
            Job.id != job.id,
            Job.is_active == True
        )
        .order_by(Job.created_at.desc())
        .limit(3)
        .all()
    )

    return render_template(
        'jobs/job_detail.html',
        job=job,
        existing_application=existing_application,
        similar_jobs=similar_jobs,
        today=date.today()
    )


@jobs_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@role_required('seeker')
def apply_job(job_id):
    """Submit a job application with resume upload and cover letter."""
    job = Job.query.get_or_404(job_id)

    if not job.is_active:
        flash("This job listing is no longer accepting applications.", "danger")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    # Check for duplicate application
    existing_application = Application.query.filter_by(
        job_id=job.id,
        seeker_id=current_user.id
    ).first()

    if existing_application:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    # Check resume upload
    if 'resume' not in request.files:
        flash("Please upload a resume file (PDF, DOC, DOCX).", "danger")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    file = request.files['resume']
    if file.filename == '':
        flash("No resume file selected. Please choose a valid file.", "danger")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    if not allowed_file(file.filename):
        flash("Unsupported file format! Allowed formats: PDF, DOC, DOCX.", "danger")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    try:
        saved_filename = save_resume_file(file, current_user.id)
    except Exception as e:
        current_app.logger.error("Error saving resume: %s", e)
        flash("Failed to upload resume. Please check file size and try again.", "danger")
        return redirect(url_for('jobs.job_detail', job_id=job.id))

    cover_letter = request.form.get('cover_letter', '').strip()

    # Create application record
    application = Application(
        job_id=job.id,
        seeker_id=current_user.id,
        resume_filename=saved_filename,
        cover_letter=cover_letter,
        status=Application.STATUS_APPLIED
    )
    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully! You can track its status in your dashboard.", "success")
    return redirect(url_for('seeker.applications'))
