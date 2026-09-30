

# 💼 JobPortal — Full-Stack Job Recruitment Web Application

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-black.svg)](https://palletsprojects.com/p/flask/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red.svg)](https://www.sqlalchemy.org/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A complete, production-quality Full-Stack Job Portal web application built with Python, Flask, Flask-SQLAlchemy, Flask-Login, SQLite, and modern Bootstrap 5. Designed to connect talent across Indian technology hubs (Pune, Mumbai, Bengaluru, Hyderabad, Chennai, Delhi NCR) with top tech employers, startups, and enterprises.

---

## 🌟 Key Features

### 👤 1. Job Seeker Module
- **Registration & Authentication**: Secure sign-up with password confirmation, duplicate email validation, and Werkzeug hashing.
- **Candidate Profile**: Manage contact info, location, professional summary, skills (with badge generation), education, and work history.
- **Job Discovery & Search**: Full-text partial matching search across job titles, descriptions, companies, and skills.
- **Multi-Parametric Filtering**: Dynamic filtering by city/location, category, job type (Full Time, Part Time, Remote, Internship, Contract), experience level, and minimum compensation.
- **Job Application Workflow**: 1-click application submission with secure resume upload (PDF, DOC, DOCX up to 16 MB) and cover letter.
- **Duplicate Prevention**: Prevents applying twice to the same job.
- **Application Tracking**: Real-time status badges (`Applied`, `Under Review`, `Shortlisted`, `Rejected`, `Hired`).
- **Secure Resume Access**: Only the candidate, hiring employer, or admin can access uploaded documents.

### 🏢 2. Employer Module
- **Company Profile**: Manage company branding, website, headquarters location, phone, and overview.
- **Job Management (CRUD)**:
  - Post new job openings with title, description, category, location, salary brackets, skills, and deadlines.
  - Edit existing job postings with immediate update reflection.
  - Delete job postings with cascade cleanup of associated applications and confirmation modals.
  - One-click Activate / Deactivate toggle to open/close vacancies without deleting.
- **Applicant Pipeline & Screening**:
  - Filter applicants by specific job opening or application status.
  - Review candidate profile, skills, education, and view cover letter notes.
  - Download candidate resumes securely.
  - Update candidate stage (`Applied` ➔ `Under Review` ➔ `Shortlisted` ➔ `Hired` / `Rejected`).

### 🛡️ 3. Administrator Console
- **System Analytics**: Platform-wide statistics on total users, seekers, employers, active/inactive jobs, and application distribution.
- **User Management**:
  - Search and filter all registered users by role and active status.
  - Activate or deactivate user accounts (deactivated accounts are immediately blocked from logging in).
  - Delete users with cascade removal of associated profiles and postings.
  - Self-protection guard prevents administrators from deactivating or deleting their own accounts.
- **Job Moderation**:
  - Inspect, filter, activate/deactivate, or delete inappropriate/spam listings across any employer.
- **Application Oversight**:
  - Global application log across all candidates and employers with status filtering and cover letter inspect modals.

### 🌐 4. REST API & External API Integration
- `GET /api/health` — System and database connectivity check.
- `GET /api/stats` — Platform high-level public metrics.
- `GET /api/categories` — Categories list with active job counts.
- `GET /api/jobs` — Paginated and filterable JSON jobs list.
- `GET /api/jobs/<id>` — Detailed job object.
- `POST /api/jobs` — Protected endpoint to create jobs (Employer/Admin auth required).
- **Graceful External API Fallback**: Optional integration with public/external jobs API feeds (e.g. Remotive). If network is unreachable or API key is absent, the system catches the exception and operates seamlessly with local database records.

### 🔒 5. Web Security & Best Practices
- **Password Security**: Irreversible Werkzeug scrypt/pbkdf2 hashing. No plaintext passwords stored.
- **Role-Based Access Control (RBAC)**: Custom `@role_required` decorator enforcing strict isolation between Seekers, Employers, and Admins.
- **File Upload Security**: Strict extension whitelist (`.pdf`, `.doc`, `.docx`), UUID-based filename sanitization preventing directory traversal, and 16 MB max-size enforcement.
- **HTTP Protection**: Secure HTTP-only cookies, Lax SameSite, custom 404, 403, and 500 error pages.

---

## 🏗️ Project Architecture

```text
job_portal/
│
├── app.py                     # Application factory, routes registration & error handlers
├── config.py                  # Environment configurations (Dev, Prod, Test)
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive documentation
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── seed.py                    # Idempotent demo database seeder
│
├── instance/
│   └── job_portal.db          # Local SQLite database (created automatically)
│
├── models/                    # SQLAlchemy ORM models
│   ├── __init__.py            # DB initialization & model exports
│   ├── user.py                # User account model with Flask-Login & roles
│   ├── profile.py             # Seeker & Employer profile attributes
│   ├── job.py                 # Job posting model with formatted helpers
│   └── application.py         # Application submission model & unique constraint
│
├── routes/                    # Flask Blueprints
│   ├── __init__.py            # Blueprint aggregations
│   ├── auth.py                # Registration, login, logout & validation
│   ├── jobs.py                # Landing page, browse, search, job details & apply
│   ├── seeker.py              # Candidate dashboard, profile, applications & resume download
│   ├── employer.py            # Employer dashboard, job CRUD & applicant management
│   ├── admin.py               # Admin analytics, user moderation & job oversight
│   └── api.py                 # JSON REST API endpoints
│
├── services/
│   ├── __init__.py
│   └── external_api.py        # Fault-tolerant external jobs integration service
│
├── utils/
│   ├── __init__.py
│   └── decorators.py          # RBAC decorator, file validators & secure upload helpers
│
├── templates/                 # Jinja2 HTML templates
│   ├── base.html              # Responsive layout with dynamic role-aware navigation
│   ├── index.html             # Homepage with hero search, stats, categories & CTAs
│   ├── 404.html               # Custom Page Not Found
│   ├── 403.html               # Custom Access Forbidden
│   ├── 500.html               # Custom Server Error
│   │
│   ├── auth/
│   │   ├── login.html         # Sign in page with demo accounts quick-fill
│   │   └── register.html      # Role selection (Seeker vs Employer) & registration
│   │
│   ├── jobs/
│   │   ├── jobs.html          # Search, filters, sort, badges & pagination
│   │   └── job_detail.html    # Full description, company info & apply modal
│   │
│   ├── seeker/
│   │   ├── dashboard.html     # Seeker metrics, recent applications & recommended jobs
│   │   ├── profile.html       # Candidate personal info, skills & live preview card
│   │   └── applications.html  # Status tracking table with filter pills & resume view
│   │
│   ├── employer/
│   │   ├── dashboard.html     # Employer metrics, recent applicants & active jobs
│   │   ├── profile.html       # Company branding & details
│   │   ├── create_job.html    # Job posting form with validation
│   │   ├── edit_job.html      # Job editor & active toggle
│   │   ├── jobs.html          # Employer manage jobs table with delete modals
│   │   └── applicants.html    # Applicant review, resume download & status updates
│   │
│   └── admin/
│       ├── dashboard.html     # Analytics counters, distribution & recent activity
│       ├── users.html         # User moderation table (search, activate/deactivate, delete)
│       ├── jobs.html          # Global job listings moderation
│       └── applications.html  # Global application audit log
│
├── static/
│   ├── css/
│   │   └── style.css          # Modern custom CSS, glassmorphism & gradients
│   ├── js/
│   │   └── script.js          # Auto-dismiss alerts, file size checks & modals
│   └── images/
│
└── uploads/
    └── resumes/               # Secure candidate resume file storage
```

---

## 💻 Tech Stack

| Layer | Technologies |
|---|---|
| **Backend** | Python 3.10+, Flask 3.1, Flask-SQLAlchemy 3.1, Flask-Login 0.6, Flask-WTF 1.3, Werkzeug |
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3.3, Bootstrap Icons 1.11.3, Google Fonts |
| **Database** | SQLite (auto-created on startup) with SQLAlchemy ORM |
| **Architecture** | Blueprint-based modular MVC with service layer |
| **Environment** | `python-dotenv`, standard library logging |

---

## 🚀 Getting Started (Run Locally)

### 1. Prerequisites
- Python 3.10, 3.11, 3.12, or 3.13 installed on your system.
- Git (optional).

### 2. Setup Virtual Environment (Recommended)

```bash
# Open PowerShell or Command Prompt in the project folder
python -m venv venv

# Activate on Windows:
venv\Scripts\activate

# (On macOS/Linux):
# source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

A `.env.example` file is provided. You can copy it to `.env`:

```bash
copy .env.example .env
```

### 5. Seed the Database with Realistic Demo Data

Run the idempotent database seed script:

```bash
python seed.py
```
> **What this does:**
> - Automatically creates database tables.
> - Creates an Administrator account.
> - Creates 4 Realistic Employers (Bengaluru, Pune, Mumbai, Hyderabad).
> - Creates 4 Job Seekers with full profiles and skills.
> - Creates 18+ comprehensive jobs across top Indian cities.
> - Creates sample applications with varied hiring stages and mock resume files.

### 6. Start the Flask Server

```bash
python app.py
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Demo Login Credentials

For quick evaluation during demonstrations, click any demo account pill on the Login page or use the credentials below:

| Role | Email Address | Password | Permissions & Notes |
|---|---|---|---|
| **Admin** | `admin@jobportal.com` | `Admin@123` | Full administrative control, user moderation, job oversight, system metrics |
| **Employer** | `techcorp@example.com` | `Employer@123` | TechCorp Solutions (Bengaluru) - Post jobs, review applicants, change statuses |
| **Employer** | `cloudwave@example.com` | `Employer@123` | CloudWave Digital (Pune) - Web & product studio |
| **Seeker** | `rohit.sharma@example.com` | `Seeker@123` | Python/Backend Developer - Track applications, edit profile, apply |
| **Seeker** | `priya.patel@example.com` | `Seeker@123` | UI/UX & Frontend Designer |

---

## 🧪 Testing Scenarios & Verification

| Test Scenario | Action Taken | Expected Result | Status |
|---|---|---|---|
| **Guest Access Control** | Navigate to `/seeker/dashboard` or `/employer/dashboard` | Redirected to `/auth/login` with warning prompt | ✅ Verified |
| **Role Isolation (Seeker)** | Seeker navigates to `/employer/dashboard` or `/admin/dashboard` | HTTP 403 Forbidden custom error page | ✅ Verified |
| **Role Isolation (Employer)** | Employer navigates to `/admin/dashboard` | HTTP 403 Forbidden custom error page | ✅ Verified |
| **Job Ownership Check** | Employer B attempts to edit/delete Employer A's job | HTTP 403 Forbidden | ✅ Verified |
| **Duplicate Application** | Seeker attempts to apply to the same job twice | Warning: "You have already applied for this job." | ✅ Verified |
| **Deactivated User** | Admin deactivates a user account, then user tries to log in | Blocked with "Your account has been deactivated" | ✅ Verified |
| **Admin Self-Protection** | Admin attempts to deactivate or delete their own account | Prevented with protective warning message | ✅ Verified |
| **Resume Upload Validation** | Uploading `.exe` or invalid file format | Blocked with error: "Unsupported file format! Allowed: PDF, DOC, DOCX" | ✅ Verified |
| **REST Health Check** | `GET /api/health` | HTTP 200 `{ "status": "ok", "database": "healthy" }` | ✅ Verified |
| **External API Fallback** | External network down or invalid API key | Logs warning, smoothly serves local DB jobs without crash | ✅ Verified |

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
|---|---|---|---|
| `GET` | `/api/health` | Health check & DB status | No |
| `GET` | `/api/stats` | Public platform summary metrics | No |
| `GET` | `/api/categories` | Industry categories with job counts | No |
| `GET` | `/api/jobs` | Search & list jobs with pagination | No |
| `GET` | `/api/jobs/<id>` | Retrieve single job details | No |
| `POST` | `/api/jobs` | Post new job opening via JSON payload | Yes (Employer/Admin) |

Example `curl` test:
```bash
curl http://127.0.0.1:5000/api/health
curl http://127.0.0.1:5000/api/categories
curl http://127.0.0.1:5000/api/jobs?keyword=Python&location=Pune
```

---

## 🚢 Deployment Guidelines

To deploy on Linux (e.g. Ubuntu with Gunicorn and Nginx):

```bash
# 1. Install Gunicorn
pip install gunicorn

# 2. Run with Gunicorn WSGI
gunicorn -w 4 -b 0.0.0.0:8000 "app:create_app('production')"
```

---

## 📄 License
This project is licensed under the MIT License — free for academic, demonstration, and commercial use.
