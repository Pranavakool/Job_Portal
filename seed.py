import os
from datetime import datetime, timezone, timedelta, date
from app import create_app
from models import db, User, Profile, Job, Application

app = create_app()


def seed_database():
    """Populate database with rich demonstration data."""
    with app.app_context():
        print("Initializing seed process...")
        db.create_all()

        # Ensure upload folder exists and create sample resumes
        upload_folder = app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)

        sample_resume_files = {
            'rohit': 'resume_sample_rohit_sharma.pdf',
            'priya': 'resume_sample_priya_patel.pdf',
            'amit': 'resume_sample_amit_verma.pdf',
            'sneha': 'resume_sample_sneha_reddy.pdf'
        }

        for key, fname in sample_resume_files.items():
            path = os.path.join(upload_folder, fname)
            if not os.path.exists(path):
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(f"%PDF-1.4\n% Mock Resume document for {key.capitalize()} in JobPortal\n"
                            f"Name: {key.capitalize()}\nExperience: Professional Developer / Engineer\n")

        # 1. Admin User
        admin_email = "admin@jobportal.com"
        admin = User.query.filter_by(email=admin_email).first()
        if not admin:
            admin = User(
                name="System Administrator",
                email=admin_email,
                role="admin",
                is_active=True
            )
            admin.set_password("Admin@123")
            db.session.add(admin)
            db.session.flush()

            admin_profile = Profile(
                user_id=admin.id,
                location="Bengaluru",
                bio="Head administrator of the JobPortal ecosystem."
            )
            db.session.add(admin_profile)
            print(f"Created Admin: {admin_email}")
        else:
            print(f"Admin already exists: {admin_email}")

        # 2. Employer Users
        employers_data = [
            {
                'email': 'techcorp@example.com',
                'name': 'TechCorp Solutions',
                'location': 'Bengaluru',
                'website': 'https://techcorp-demo.in',
                'phone': '+91 80 4123 4567',
                'bio': 'Next-generation cloud infrastructure and enterprise software engineering powerhouse based in Bengaluru.'
            },
            {
                'email': 'cloudwave@example.com',
                'name': 'CloudWave Digital',
                'location': 'Pune',
                'website': 'https://cloudwave-pune.demo',
                'phone': '+91 20 6789 1234',
                'bio': 'Pioneering scalable web applications, API services, and modern SaaS products for global markets.'
            },
            {
                'email': 'finpulse@example.com',
                'name': 'FinPulse Capital',
                'location': 'Mumbai',
                'website': 'https://finpulse-capital.demo',
                'phone': '+91 22 8901 2345',
                'bio': 'Leading Indian FinTech innovators building high-frequency algorithmic trading, payments, and risk management systems.'
            },
            {
                'email': 'zenithhealth@example.com',
                'name': 'Zenith Health AI',
                'location': 'Hyderabad',
                'website': 'https://zenithhealth-ai.demo',
                'phone': '+91 40 5555 7890',
                'bio': 'Biotech and digital health platform empowering hospitals and diagnostics through artificial intelligence.'
            }
        ]

        employer_instances = {}
        for ed in employers_data:
            emp = User.query.filter_by(email=ed['email']).first()
            if not emp:
                emp = User(
                    name=ed['name'],
                    email=ed['email'],
                    role='employer',
                    is_active=True
                )
                emp.set_password('Employer@123')
                db.session.add(emp)
                db.session.flush()

                prof = Profile(
                    user_id=emp.id,
                    company_name=ed['name'],
                    company_website=ed['website'],
                    location=ed['location'],
                    phone=ed['phone'],
                    bio=ed['bio']
                )
                db.session.add(prof)
                print(f"Created Employer: {ed['email']}")
            employer_instances[ed['email']] = emp

        # 3. Job Seeker Users
        seekers_data = [
            {
                'email': 'rohit.sharma@example.com',
                'name': 'Rohit Sharma',
                'location': 'Pune',
                'phone': '+91 98201 23456',
                'skills': 'Python, Flask, Django, PostgreSQL, Docker, REST APIs',
                'education': 'B.Tech in Computer Engineering, COEP Pune (2022)',
                'experience': '3 years developing resilient backend microservices at a Pune product studio.',
                'bio': 'Passionate backend software engineer dedicated to building scalable web services and databases.',
                'resume_key': 'rohit'
            },
            {
                'email': 'priya.patel@example.com',
                'name': 'Priya Patel',
                'location': 'Mumbai',
                'phone': '+91 98192 34567',
                'skills': 'Figma, UI/UX, React, JavaScript, HTML5, CSS3, Bootstrap',
                'education': 'Bachelor of Design (B.Des), NID Ahmedabad (2021)',
                'experience': '4 years designing engaging mobile & web products and human-centered user experiences.',
                'bio': 'Design-focused frontend technologist bridging the gap between aesthetic design and clean code.',
                'resume_key': 'priya'
            },
            {
                'email': 'amit.verma@example.com',
                'name': 'Amit Verma',
                'location': 'Bengaluru',
                'phone': '+91 99001 87654',
                'skills': 'AWS, Kubernetes, Terraform, Linux, CI/CD, Python, Prometheus',
                'education': 'M.Tech in Information Technology, IIIT Bangalore (2020)',
                'experience': '5 years architecting zero-downtime cloud infrastructure and DevOps deployment pipelines.',
                'bio': 'DevOps & Site Reliability Engineer passionate about automated delivery and distributed systems.',
                'resume_key': 'amit'
            },
            {
                'email': 'sneha.reddy@example.com',
                'name': 'Sneha Reddy',
                'location': 'Hyderabad',
                'phone': '+91 97002 45678',
                'skills': 'Python, Machine Learning, PyTorch, SQL, Pandas, Tableau',
                'education': 'B.Tech in Artificial Intelligence & Data Science, IIT Hyderabad (2023)',
                'experience': '2 years analyzing high-volume datasets and training neural predictive models.',
                'bio': 'Data Scientist eager to solve high-impact analytics and machine learning challenges.',
                'resume_key': 'sneha'
            }
        ]

        seeker_instances = {}
        for sd in seekers_data:
            sk = User.query.filter_by(email=sd['email']).first()
            if not sk:
                sk = User(
                    name=sd['name'],
                    email=sd['email'],
                    role='seeker',
                    is_active=True
                )
                sk.set_password('Seeker@123')
                db.session.add(sk)
                db.session.flush()

                prof = Profile(
                    user_id=sk.id,
                    location=sd['location'],
                    phone=sd['phone'],
                    skills=sd['skills'],
                    education=sd['education'],
                    experience=sd['experience'],
                    bio=sd['bio']
                )
                db.session.add(prof)
                print(f"Created Seeker: {sd['email']}")
            seeker_instances[sd['email']] = sk

        db.session.commit()

        # 4. Realistic Jobs (18+ jobs across Pune, Mumbai, Bengaluru, Hyderabad, Chennai, Delhi NCR, Noida, Gurugram)
        jobs_dataset = [
            {
                'employer_email': 'techcorp@example.com',
                'title': 'Senior Python Backend Engineer',
                'company': 'TechCorp Solutions',
                'category': 'IT & Software',
                'location': 'Bengaluru',
                'job_type': 'Full Time',
                'experience_level': 'Senior Level',
                'salary_min': 1400000,
                'salary_max': 2400000,
                'skills': 'Python, Flask, FastAPI, PostgreSQL, Redis, Docker',
                'deadline': date.today() + timedelta(days=30),
                'description': 'We are seeking an experienced Senior Python Engineer to architect high-throughput microservices. You will lead system design, optimize database queries, and mentor team members in modern Python asynchronous patterns.'
            },
            {
                'employer_email': 'techcorp@example.com',
                'title': 'Cloud DevOps & Kubernetes Specialist',
                'company': 'TechCorp Solutions',
                'category': 'Engineering',
                'location': 'Bengaluru',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 1200000,
                'salary_max': 1800000,
                'skills': 'Kubernetes, AWS, Terraform, GitHub Actions, Linux',
                'deadline': date.today() + timedelta(days=45),
                'description': 'Join our infrastructure squad to automate multi-region cloud deployments on AWS. Responsible for maintaining Kubernetes clusters, building CI/CD pipelines, and ensuring 99.99% system availability.'
            },
            {
                'employer_email': 'techcorp@example.com',
                'title': 'Full-Stack JavaScript/Python Developer',
                'company': 'TechCorp Solutions',
                'category': 'IT & Software',
                'location': 'Remote',
                'job_type': 'Remote',
                'experience_level': 'Mid Level',
                'salary_min': 900000,
                'salary_max': 1500000,
                'skills': 'Python, Flask, React, TypeScript, HTML5, CSS3',
                'deadline': date.today() + timedelta(days=25),
                'description': 'Exciting remote opportunity for a versatile full-stack engineer. Build responsive customer-facing web applications alongside robust Python APIs. Flexible work hours and remote setup allowance provided.'
            },
            {
                'employer_email': 'cloudwave@example.com',
                'title': 'Python / Django Web Developer',
                'company': 'CloudWave Digital',
                'category': 'IT & Software',
                'location': 'Pune',
                'job_type': 'Full Time',
                'experience_level': 'Entry Level',
                'salary_min': 600000,
                'salary_max': 900000,
                'skills': 'Python, Django, SQLite, Bootstrap, RESTful APIs',
                'deadline': date.today() + timedelta(days=20),
                'description': 'Ideal opening for energetic graduates or junior engineers with hands-on Python experience. Develop features for our flagship B2B web applications in Pune with competitive perks and comprehensive mentorship.'
            },
            {
                'employer_email': 'cloudwave@example.com',
                'title': 'Lead UI/UX Product Designer',
                'company': 'CloudWave Digital',
                'category': 'Design & Creative',
                'location': 'Pune',
                'job_type': 'Full Time',
                'experience_level': 'Lead / Manager',
                'salary_min': 1500000,
                'salary_max': 2200000,
                'skills': 'Figma, Design Systems, User Research, Prototyping, Wireframing',
                'deadline': date.today() + timedelta(days=35),
                'description': 'Lead our product design vision. You will craft intuitive wireframes, interactive prototypes, and design systems for enterprise web portals, conducting usability testing across desktop and mobile devices.'
            },
            {
                'employer_email': 'cloudwave@example.com',
                'title': 'Software Engineering Intern (Summer 2026)',
                'company': 'CloudWave Digital',
                'category': 'IT & Software',
                'location': 'Pune',
                'job_type': 'Internship',
                'experience_level': 'Entry Level',
                'salary_min': 300000,
                'salary_max': 450000,
                'skills': 'Python, Git, Problem Solving, Data Structures',
                'deadline': date.today() + timedelta(days=15),
                'description': 'Fast-track your tech career with our 6-month paid engineering internship in Pune. Learn production software development, work on real client features, and earn a potential full-time pre-placement offer.'
            },
            {
                'employer_email': 'finpulse@example.com',
                'title': 'Quantitative Risk Analyst',
                'company': 'FinPulse Capital',
                'category': 'Finance & Banking',
                'location': 'Mumbai',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 1300000,
                'salary_max': 2000000,
                'skills': 'Financial Modeling, Python, SQL, Statistics, Risk Assessment',
                'deadline': date.today() + timedelta(days=40),
                'description': 'Analyze market volatility, portfolio risk exposure, and trading strategies in Mumbai’s bustling financial hub. Utilize quantitative Python scripts and statistical tools to deliver actionable insights to fund managers.'
            },
            {
                'employer_email': 'finpulse@example.com',
                'title': 'FinTech Security & Compliance Manager',
                'company': 'FinPulse Capital',
                'category': 'Finance & Banking',
                'location': 'Mumbai',
                'job_type': 'Full Time',
                'experience_level': 'Senior Level',
                'salary_min': 1800000,
                'salary_max': 2800000,
                'skills': 'Information Security, RBI Guidelines, SOC2, Audit, PCI-DSS',
                'deadline': date.today() + timedelta(days=50),
                'description': 'Spearhead regulatory compliance and digital security architecture for banking integrations. Collaborate with engineering to safeguard transaction endpoints and ensure full compliance with RBI policies.'
            },
            {
                'employer_email': 'finpulse@example.com',
                'title': 'Corporate Financial Analyst',
                'company': 'FinPulse Capital',
                'category': 'Finance & Banking',
                'location': 'Mumbai',
                'job_type': 'Full Time',
                'experience_level': 'Entry Level',
                'salary_min': 700000,
                'salary_max': 1100000,
                'skills': 'Excel, Financial Statements, Budgeting, Forecasting',
                'deadline': date.today() + timedelta(days=28),
                'description': 'Conduct variance analysis, prepare quarterly corporate performance decks, and support budgeting for expansion across Tier-1 Indian markets.'
            },
            {
                'employer_email': 'zenithhealth@example.com',
                'title': 'Data Scientist & Machine Learning Engineer',
                'company': 'Zenith Health AI',
                'category': 'Healthcare',
                'location': 'Hyderabad',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 1300000,
                'salary_max': 2100000,
                'skills': 'Python, PyTorch, Scikit-Learn, NLP, Healthcare Analytics',
                'deadline': date.today() + timedelta(days=35),
                'description': 'Build predictive machine learning models to assist clinicians with diagnostic analysis. You will train medical NLP models and deploy models via secure RESTful APIs in HITEC City, Hyderabad.'
            },
            {
                'employer_email': 'zenithhealth@example.com',
                'title': 'Clinical Operations & Quality Associate',
                'company': 'Zenith Health AI',
                'category': 'Healthcare',
                'location': 'Hyderabad',
                'job_type': 'Full Time',
                'experience_level': 'Entry Level',
                'salary_min': 550000,
                'salary_max': 850000,
                'skills': 'Clinical Data, Healthcare SOPs, Quality Assurance, Documentation',
                'deadline': date.today() + timedelta(days=21),
                'description': 'Coordinate clinical trial documentation, evaluate diagnostic accuracy metrics, and partner with hospital stakeholders to implement automated healthcare platforms.'
            },
            {
                'employer_email': 'zenithhealth@example.com',
                'title': 'Healthcare Sales & Hospital Partnerships Manager',
                'company': 'Zenith Health AI',
                'category': 'Marketing & Sales',
                'location': 'Hyderabad',
                'job_type': 'Full Time',
                'experience_level': 'Senior Level',
                'salary_min': 1100000,
                'salary_max': 1800000,
                'skills': 'B2B Sales, Hospital Partnerships, Client Relations, Healthcare Tech',
                'deadline': date.today() + timedelta(days=45),
                'description': 'Drive commercial expansion by partnering with private hospital chains and diagnostic centers across South India. Build lasting relationships with chief medical officers and hospital administrators.'
            },
            {
                'employer_email': 'techcorp@example.com',
                'title': 'Talent Acquisition & HR Specialist',
                'company': 'TechCorp Solutions',
                'category': 'Human Resources',
                'location': 'Bengaluru',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 650000,
                'salary_max': 1050000,
                'skills': 'Technical Recruiting, LinkedIn Recruiter, Candidate Sourcing, HR Operations',
                'deadline': date.today() + timedelta(days=30),
                'description': 'Lead end-to-end recruitment for high-caliber engineering and product positions. Manage candidate experience, organize campus hiring drives, and streamline onboarding pipelines.'
            },
            {
                'employer_email': 'cloudwave@example.com',
                'title': 'Digital Marketing & SEO Strategist',
                'company': 'CloudWave Digital',
                'category': 'Marketing & Sales',
                'location': 'Pune',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 600000,
                'salary_max': 950000,
                'skills': 'SEO, Google Analytics, Content Strategy, SEM, Social Media Marketing',
                'deadline': date.today() + timedelta(days=30),
                'description': 'Drive organic search traffic and inbound lead generation for SaaS solutions. Create content calendars, optimize landing pages, and run high-ROI digital ad campaigns.'
            },
            {
                'employer_email': 'techcorp@example.com',
                'title': 'Site Reliability Engineer (Contract)',
                'company': 'TechCorp Solutions',
                'category': 'Engineering',
                'location': 'Chennai',
                'job_type': 'Contract',
                'experience_level': 'Senior Level',
                'salary_min': 1500000,
                'salary_max': 2200000,
                'skills': 'SRE, Linux, Monitoring, Grafana, Incident Response, Shell Scripting',
                'deadline': date.today() + timedelta(days=60),
                'description': '12-month renewable contract for a battle-tested SRE to strengthen system resilience and disaster recovery across hybrid cloud infrastructures in Chennai.'
            },
            {
                'employer_email': 'cloudwave@example.com',
                'title': 'Part-Time Technical Content Writer',
                'company': 'CloudWave Digital',
                'category': 'Design & Creative',
                'location': 'Delhi NCR',
                'job_type': 'Part Time',
                'experience_level': 'Entry Level',
                'salary_min': 350000,
                'salary_max': 500000,
                'skills': 'Technical Writing, Blogging, API Documentation, Markdown',
                'deadline': date.today() + timedelta(days=25),
                'description': 'Write engaging technical blog posts, developer guides, and API documentation. 20 hours per week with flexible schedule and remote coordination.'
            },
            {
                'employer_email': 'finpulse@example.com',
                'title': 'Enterprise Account Executive',
                'company': 'FinPulse Capital',
                'category': 'Marketing & Sales',
                'location': 'Gurugram',
                'job_type': 'Full Time',
                'experience_level': 'Mid Level',
                'salary_min': 1000000,
                'salary_max': 1600000,
                'skills': 'Enterprise Sales, Negotiation, B2B SaaS, CRM, Presentation',
                'deadline': date.today() + timedelta(days=35),
                'description': 'Accelerate revenue growth by closing enterprise contracts with NBFCs and digital lending firms across Northern India from our Gurugram office.'
            },
            {
                'employer_email': 'zenithhealth@example.com',
                'title': 'AI Research Scientist (Computer Vision)',
                'company': 'Zenith Health AI',
                'category': 'Healthcare',
                'location': 'Hyderabad',
                'job_type': 'Full Time',
                'experience_level': 'Senior Level',
                'salary_min': 2000000,
                'salary_max': 3200000,
                'skills': 'Computer Vision, Deep Learning, PyTorch, Medical Imaging (DICOM), OpenCV',
                'deadline': date.today() + timedelta(days=60),
                'description': 'Lead foundational research into medical imaging models (CT scans, X-rays, MRI). Collaborate with academic institutions and publish groundbreaking healthcare AI advancements.'
            }
        ]

        created_jobs = []
        for jd in jobs_dataset:
            emp = employer_instances.get(jd['employer_email'])
            if not emp:
                continue

            existing_job = Job.query.filter_by(
                employer_id=emp.id,
                title=jd['title'],
                company=jd['company']
            ).first()

            if not existing_job:
                job = Job(
                    employer_id=emp.id,
                    title=jd['title'],
                    company=jd['company'],
                    category=jd['category'],
                    location=jd['location'],
                    job_type=jd['job_type'],
                    experience_level=jd['experience_level'],
                    salary_min=jd['salary_min'],
                    salary_max=jd['salary_max'],
                    skills=jd['skills'],
                    deadline=jd['deadline'],
                    description=jd['description'],
                    is_active=True
                )
                db.session.add(job)
                db.session.flush()
                print(f"Created Job: {jd['title']} at {jd['company']}")
                created_jobs.append(job)
            else:
                created_jobs.append(existing_job)

        db.session.commit()

        # 5. Sample Applications across candidates and jobs
        sample_applications = [
            {
                'seeker_email': 'rohit.sharma@example.com',
                'job_title': 'Senior Python Backend Engineer',
                'resume_file': 'resume_sample_rohit_sharma.pdf',
                'cover_letter': 'Dear Hiring Team, with over 3 years of building performant Flask/Django microservices and PostgreSQL architectures, I am excited about contributing to TechCorp\'s backend infrastructure.',
                'status': Application.STATUS_SHORTLISTED
            },
            {
                'seeker_email': 'rohit.sharma@example.com',
                'job_title': 'Python / Django Web Developer',
                'resume_file': 'resume_sample_rohit_sharma.pdf',
                'cover_letter': 'Hello CloudWave team, I have hands-on experience deploying clean Django apps in Pune and would love to bring my software engineering passion to your product studio.',
                'status': Application.STATUS_HIRED
            },
            {
                'seeker_email': 'priya.patel@example.com',
                'job_title': 'Lead UI/UX Product Designer',
                'resume_file': 'resume_sample_priya_patel.pdf',
                'cover_letter': 'Hi CloudWave team! Having led end-to-end design systems in Figma and prototyped clean web interfaces, I am eager to shape the UI/UX vision for your products.',
                'status': Application.STATUS_UNDER_REVIEW
            },
            {
                'seeker_email': 'amit.verma@example.com',
                'job_title': 'Cloud DevOps & Kubernetes Specialist',
                'resume_file': 'resume_sample_amit_verma.pdf',
                'cover_letter': 'Dear TechCorp team, I specialize in production Kubernetes clusters, AWS cloud cost-optimization, and automated GitOps CI/CD delivery pipelines.',
                'status': Application.STATUS_APPLIED
            },
            {
                'seeker_email': 'sneha.reddy@example.com',
                'job_title': 'Data Scientist & Machine Learning Engineer',
                'resume_file': 'resume_sample_sneha_reddy.pdf',
                'cover_letter': 'Dear Zenith Health AI recruiters, my background in PyTorch and healthcare analytics aligns directly with your mission to empower clinical diagnostics.',
                'status': Application.STATUS_SHORTLISTED
            }
        ]

        for app_data in sample_applications:
            seeker = seeker_instances.get(app_data['seeker_email'])
            job = next((j for j in created_jobs if j.title == app_data['job_title']), None)
            if seeker and job:
                existing_app = Application.query.filter_by(
                    job_id=job.id,
                    seeker_id=seeker.id
                ).first()

                if not existing_app:
                    application = Application(
                        job_id=job.id,
                        seeker_id=seeker.id,
                        resume_filename=app_data['resume_file'],
                        cover_letter=app_data['cover_letter'],
                        status=app_data['status']
                    )
                    db.session.add(application)
                    print(f"Created Application: {seeker.name} -> {job.title} ({app_data['status']})")

        db.session.commit()
        print("\nDatabase seeded successfully!")
        print("Demo Credentials:")
        print("  Admin:     admin@jobportal.com / Admin@123")
        print("  Employer:  techcorp@example.com / Employer@123")
        print("  Seeker:    rohit.sharma@example.com / Seeker@123")


if __name__ == '__main__':
    seed_database()
