import logging
import requests
from flask import current_app

logger = logging.getLogger(__name__)


class ExternalJobService:
    """
    Service for integrating optional external job feeds.
    Fault-tolerant: always catches exceptions and returns empty list or fallback,
    never crashing the primary application or blocking local DB jobs.
    """

    @staticmethod
    def fetch_jobs(keyword: str = None, location: str = None, limit: int = 5) -> list:
        """
        Fetch external jobs from a public API if configured and available.
        Returns a list of normalized job dicts marked with is_external=True.
        """
        api_enabled = current_app.config.get('EXTERNAL_API_ENABLED', True)
        if not api_enabled:
            return []

        api_key = current_app.config.get('JOB_API_KEY', '').strip()

        # We attempt to query a free public jobs endpoint (e.g. Remotive remote jobs) with strict 3s timeout
        url = "https://remotive.com/api/remote-jobs"
        params = {"limit": limit}
        if keyword:
            params["search"] = keyword

        headers = {
            "User-Agent": "JobPortal-Academic-Demo/1.0"
        }
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        try:
            response = requests.get(url, params=params, headers=headers, timeout=3.0)
            if response.status_code == 200:
                data = response.json()
                raw_jobs = data.get('jobs', [])
                normalized_jobs = []

                for rj in raw_jobs[:limit]:
                    normalized_jobs.append({
                        'id': f"ext-{rj.get('id')}",
                        'title': rj.get('title', 'External Opportunity'),
                        'company': rj.get('company_name', 'External Partner'),
                        'category': rj.get('category', 'Technology'),
                        'location': rj.get('candidate_required_location', 'Remote (Worldwide)'),
                        'job_type': rj.get('job_type', 'Full Time').replace('_', ' ').title(),
                        'experience_level': 'Mid Level',
                        'salary_display': rj.get('salary', 'Competitive / Commensurate with experience') or 'Competitive',
                        'description': rj.get('description', 'External job listing.'),
                        'skills': ', '.join(rj.get('tags', [])) if rj.get('tags') else 'Remote, Tech',
                        'skills_list': rj.get('tags', ['Remote']),
                        'url': rj.get('url', '#'),
                        'is_external': True,
                        'is_active': True,
                        'created_at': rj.get('publication_date', 'Recently')
                    })
                return normalized_jobs
            else:
                logger.warning("External job API returned status code %s", response.status_code)
                return []
        except requests.exceptions.RequestException as e:
            logger.info("External jobs API query skipped or timed out (%s). Using local jobs exclusively.", e)
            return []
        except Exception as e:
            logger.warning("Unexpected error fetching external jobs: %s", e)
            return []
