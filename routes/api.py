from datetime import datetime, timezone
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user
from sqlalchemy import or_, func
from models import db, Job, Application, User
from routes.jobs import POPULAR_CATEGORIES

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint to verify system and database connectivity."""
    db_status = "healthy"
    try:
        db.session.execute(db.select(1))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"

    return jsonify({
        'status': 'ok' if db_status == "healthy" else "degraded",
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'database': db_status,
        'environment': current_app.config.get('ENV', 'development'),
        'version': '1.0.0'
    }), (200 if db_status == "healthy" else 500)


@api_bp.route('/stats', methods=['GET'])
def stats():
    """Public platform metrics."""
    return jsonify({
        'success': True,
        'data': {
            'active_jobs': Job.query.filter_by(is_active=True).count(),
            'total_seekers': User.query.filter_by(role='seeker', is_active=True).count(),
            'total_employers': User.query.filter_by(role='employer', is_active=True).count(),
            'total_applications': Application.query.count()
        }
    }), 200


@api_bp.route('/categories', methods=['GET'])
def categories():
    """Get all job categories along with active job counts."""
    counts = dict(
        db.session.query(Job.category, func.count(Job.id))
        .filter(Job.is_active == True)
        .group_by(Job.category)
        .all()
    )

    result = []
    for cat in POPULAR_CATEGORIES:
        result.append({
            'name': cat,
            'job_count': counts.get(cat, 0)
        })

    return jsonify({
        'success': True,
        'count': len(result),
        'categories': result
    }), 200


@api_bp.route('/jobs', methods=['GET'])
def get_jobs():
    """List and search active jobs with pagination."""
    keyword = request.args.get('keyword', '').strip()
    location = request.args.get('location', '').strip()
    category = request.args.get('category', '').strip()
    job_type = request.args.get('job_type', '').strip()
    page = request.args.get('page', 1, type=int)
    limit = min(request.args.get('limit', 10, type=int), 50)

    query = Job.query.filter_by(is_active=True)

    if keyword:
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                Job.title.ilike(pattern),
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

    pagination = query.order_by(Job.created_at.desc()).paginate(page=page, per_page=limit, error_out=False)

    return jsonify({
        'success': True,
        'page': pagination.page,
        'pages': pagination.pages,
        'total': pagination.total,
        'jobs': [j.to_dict() for j in pagination.items]
    }), 200


@api_bp.route('/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    """Retrieve full details for a single job."""
    job = db.session.get(Job, job_id)
    if not job or not job.is_active:
        return jsonify({
            'success': False,
            'error': 'Job not found or is no longer active'
        }), 404

    return jsonify({
        'success': True,
        'job': job.to_dict()
    }), 200


@api_bp.route('/jobs', methods=['POST'])
def create_job():
    """
    Create a new job posting via API.
    Protected: Must be authenticated as an employer or admin.
    """
    if not current_user.is_authenticated:
        return jsonify({'success': False, 'error': 'Authentication required'}), 401

    if not (current_user.is_employer or current_user.is_admin):
        return jsonify({'success': False, 'error': 'Only employers or admins can post jobs'}), 403

    data = request.get_json() or {}

    title = data.get('title', '').strip()
    company = data.get('company', '').strip() or current_user.name
    category = data.get('category', '').strip()
    location = data.get('location', '').strip()
    description = data.get('description', '').strip()

    if not all([title, company, category, location, description]):
        return jsonify({
            'success': False,
            'error': 'Missing required fields: title, company, category, location, description'
        }), 400

    new_job = Job(
        employer_id=current_user.id,
        title=title,
        company=company,
        category=category,
        location=location,
        description=description,
        job_type=data.get('job_type', 'Full Time'),
        experience_level=data.get('experience_level', 'Entry Level'),
        salary_min=data.get('salary_min'),
        salary_max=data.get('salary_max'),
        skills=data.get('skills', ''),
        is_active=True
    )

    db.session.add(new_job)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Job posted successfully',
        'job': new_job.to_dict()
    }), 201
