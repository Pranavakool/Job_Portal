import io
import unittest
from app import create_app
from models import db, User, Job, Application, Profile


class JobPortalTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create demo admin
        self.admin = User(name="Test Admin", email="admin_test@portal.com", role="admin", is_active=True)
        self.admin.set_password("Admin@123")
        db.session.add(self.admin)

        # Create demo employer 1
        self.employer1 = User(name="TechCorp Demo", email="emp1@test.com", role="employer", is_active=True)
        self.employer1.set_password("Emp@123")
        db.session.add(self.employer1)
        db.session.flush()
        p1 = Profile(user_id=self.employer1.id, company_name="TechCorp Demo", location="Bengaluru")
        db.session.add(p1)

        # Create demo employer 2
        self.employer2 = User(name="CloudWave Demo", email="emp2@test.com", role="employer", is_active=True)
        self.employer2.set_password("Emp@123")
        db.session.add(self.employer2)
        db.session.flush()
        p2 = Profile(user_id=self.employer2.id, company_name="CloudWave Demo", location="Pune")
        db.session.add(p2)

        # Create demo seeker
        self.seeker = User(name="Rahul Test", email="seeker@test.com", role="seeker", is_active=True)
        self.seeker.set_password("Seeker@123")
        db.session.add(self.seeker)
        db.session.flush()
        ps = Profile(user_id=self.seeker.id, location="Pune", skills="Python, Flask")
        db.session.add(ps)

        # Create job by employer 1
        self.job1 = Job(
            employer_id=self.employer1.id,
            title="Python Developer",
            company="TechCorp Demo",
            category="IT & Software",
            location="Bengaluru",
            job_type="Full Time",
            experience_level="Mid Level",
            salary_min=1000000,
            salary_max=1500000,
            skills="Python, Flask",
            description="Build resilient APIs and backend pipelines.",
            is_active=True
        )
        db.session.add(self.job1)

        # Create job by employer 2
        self.job2 = Job(
            employer_id=self.employer2.id,
            title="Frontend Designer",
            company="CloudWave Demo",
            category="Design & Creative",
            location="Pune",
            job_type="Full Time",
            experience_level="Entry Level",
            description="Design responsive web layouts and design systems.",
            is_active=True
        )
        db.session.add(self.job2)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)

    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)

    # 1. API Endpoints
    def test_api_health(self):
        res = self.client.get('/api/health')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['status'], 'ok')

    def test_api_jobs_and_categories(self):
        res = self.client.get('/api/jobs')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data['total'], 2)

        cat_res = self.client.get('/api/categories')
        self.assertEqual(cat_res.status_code, 200)
        cat_data = cat_res.get_json()
        self.assertTrue(cat_data['success'])

    # 2. Public Pages
    def test_public_pages(self):
        home_res = self.client.get('/')
        self.assertEqual(home_res.status_code, 200)
        self.assertIn(b'JobPortal', home_res.data)

        jobs_res = self.client.get('/jobs?keyword=Python')
        self.assertEqual(jobs_res.status_code, 200)
        self.assertIn(b'Python Developer', jobs_res.data)

        detail_res = self.client.get(f'/jobs/{self.job1.id}')
        self.assertEqual(detail_res.status_code, 200)
        self.assertIn(b'TechCorp Demo', detail_res.data)

    # 3. Registration Rules
    def test_registration_security(self):
        # Register seeker -> success
        res = self.client.post('/auth/register', data={
            'name': 'New Candidate',
            'email': 'new_seeker@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'role': 'seeker'
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Registration successful', res.data)

        # Attempt to register as admin -> rejected!
        res_admin = self.client.post('/auth/register', data={
            'name': 'Fake Admin',
            'email': 'fake_admin@example.com',
            'password': 'Password123',
            'confirm_password': 'Password123',
            'role': 'admin'
        }, follow_redirects=True)
        self.assertIn(b'Invalid account type selected', res_admin.data)

    # 4. Role-Based Access Control
    def test_rbac_protections(self):
        # Unauthenticated guest accessing seeker dashboard -> redirected to login
        res = self.client.get('/seeker/dashboard')
        self.assertEqual(res.status_code, 302)
        self.assertIn('/auth/login', res.headers['Location'])

        # Seeker accessing employer dashboard -> 403
        self.login('seeker@test.com', 'Seeker@123')
        res_emp_dash = self.client.get('/employer/dashboard')
        self.assertEqual(res_emp_dash.status_code, 403)

        # Seeker accessing admin dashboard -> 403
        res_admin_dash = self.client.get('/admin/dashboard')
        self.assertEqual(res_admin_dash.status_code, 403)
        self.logout()

        # Employer accessing admin dashboard -> 403
        self.login('emp1@test.com', 'Emp@123')
        res_admin_emp = self.client.get('/admin/dashboard')
        self.assertEqual(res_admin_emp.status_code, 403)

        # Employer 1 attempting to edit Employer 2's job -> 403
        res_edit_other = self.client.get(f'/employer/jobs/{self.job2.id}/edit')
        self.assertEqual(res_edit_other.status_code, 403)
        self.logout()

    # 5. Job Application & Duplicate Check
    def test_job_application_and_duplicate(self):
        self.login('seeker@test.com', 'Seeker@123')

        # Apply with valid mock resume file
        resume_data = (io.BytesIO(b"%PDF-1.4 Mock resume content"), "resume.pdf")
        apply_res = self.client.post(
            f'/jobs/{self.job1.id}/apply',
            data={'resume': resume_data, 'cover_letter': 'Excited to apply!'},
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertEqual(apply_res.status_code, 200)
        self.assertIn(b'Application submitted successfully', apply_res.data)

        # Try to apply again -> blocked!
        resume_data2 = (io.BytesIO(b"%PDF-1.4 Mock resume content 2"), "resume.pdf")
        duplicate_res = self.client.post(
            f'/jobs/{self.job1.id}/apply',
            data={'resume': resume_data2, 'cover_letter': 'Trying again!'},
            content_type='multipart/form-data',
            follow_redirects=True
        )
        self.assertIn(b'You have already applied for this job', duplicate_res.data)
        self.logout()

    # 6. Employer Applicant Management
    def test_employer_applicant_flow(self):
        # Create an application
        app_record = Application(
            job_id=self.job1.id,
            seeker_id=self.seeker.id,
            resume_filename='test_resume.pdf',
            status=Application.STATUS_APPLIED
        )
        db.session.add(app_record)
        db.session.commit()

        # Login as Employer 1 and update status
        self.login('emp1@test.com', 'Emp@123')
        stat_res = self.client.post(
            f'/employer/applications/{app_record.id}/status',
            data={'status': 'Shortlisted'},
            follow_redirects=True
        )
        self.assertEqual(stat_res.status_code, 200)
        self.assertIn(b'updated to', stat_res.data)

        updated_app = db.session.get(Application, app_record.id)
        self.assertEqual(updated_app.status, 'Shortlisted')
        self.logout()

    # 7. Admin Controls & Self-Protection
    def test_admin_protections(self):
        self.login('admin_test@portal.com', 'Admin@123')

        # Admin attempts to deactivate self -> blocked!
        deact_res = self.client.post(f'/admin/users/{self.admin.id}/toggle-status', follow_redirects=True)
        self.assertIn(b'cannot deactivate your own active admin', deact_res.data)

        # Admin deactivates test seeker
        self.client.post(f'/admin/users/{self.seeker.id}/toggle-status', follow_redirects=True)
        deactivated_seeker = db.session.get(User, self.seeker.id)
        self.assertFalse(deactivated_seeker.is_active)
        self.logout()

        # Deactivated seeker tries to login -> blocked!
        login_res = self.login('seeker@test.com', 'Seeker@123')
        self.assertIn(b'account has been deactivated', login_res.data)


if __name__ == '__main__':
    unittest.main()
