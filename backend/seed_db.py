"""
Database seeding script to populate the database with comprehensive sample data
for development and testing.

Run this script from the backend directory with: python seed_db.py
"""

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import (
    Student, User, WeeklySkillScore, Attendance, 
    Course, Module, Lesson, Enrollment, LessonProgress,
    Quiz, QuizSubmission, Badge, StudentBadge
)
from models.quiz import AnswerChoice
from models.badge import BadgeConditionType
from services.auth import hash_password
import random

# ============================================================================
# STUDENT DATA (50+ students)
# ============================================================================
STUDENT_NAMES = [
    "Aarav Patel", "Bhavna Sharma", "Chirag Verma", "Divya Gupta", "Eshan Kumar",
    "Fatima Khan", "Ganesh Singh", "Harsh Malhotra", "Ishita Reddy", "Jiya Kapoor",
    "Karan Nair", "Laxmi Rao", "Madhav Desai", "Neha Menon", "Omkar Tiwari",
    "Priya Saxena", "Quentin Das", "Ravi Sharma", "Sneha Pandey", "Tanvi Joshi",
    "Umesh Chandra", "Vidya Krishnan", "Wasim Ahmed", "Xena Dsouza", "Yash Agarwal",
    "Zara Hussain", "Arjun Mehta", "Bhumi Patel", "Chetan Yadav", "Deepika Nair",
    "Ekta Sharma", "Farhan Ali", "Gayatri Pillai", "Hitesh Gupta", "Isha Verma",
    "Jai Prakash", "Kavitha Menon", "Lokesh Reddy", "Meera Singh", "Naveen Kumar",
    "Ojas Sharma", "Pooja Pandey", "Qasim Sheikh", "Ritu Malhotra", "Sanjay Tiwari",
    "Tara Desai", "Urvashi Kapoor", "Vikram Joshi", "Wriddhiman Sen", "Yamini Rao",
    "Zubin Contractor", "Akshay Kulkarni", "Bindu Raghavan", "Chandni Sethi"
]

TRACKS = ["Engineering", "Data Science", "Design", "Product Management", "Business Analytics"]

# ============================================================================
# COURSE DATA (15+ courses)
# ============================================================================
COURSES_DATA = [
    {
        "title": "Python Programming Fundamentals",
        "description": "Learn Python from scratch with hands-on projects and real-world applications.",
        "track_type": "Engineering",
        "level": "beginner",
        "modules": [
            {
                "title": "Getting Started with Python",
                "lessons": [
                    {"title": "Introduction to Python", "content": "Python is a high-level, interpreted programming language known for its simplicity and readability.", "duration": 15},
                    {"title": "Setting Up Your Environment", "content": "Learn how to install Python and set up your development environment.", "duration": 20},
                    {"title": "Your First Python Program", "content": "Write your first 'Hello World' program and understand basic syntax.", "duration": 25},
                ]
            },
            {
                "title": "Data Types and Variables",
                "lessons": [
                    {"title": "Variables and Naming", "content": "Understand how to declare variables and best practices for naming.", "duration": 20},
                    {"title": "Numbers and Strings", "content": "Work with integers, floats, and string data types.", "duration": 25},
                    {"title": "Lists and Tuples", "content": "Learn about sequence data types in Python.", "duration": 30},
                ]
            },
            {
                "title": "Control Flow",
                "lessons": [
                    {"title": "Conditional Statements", "content": "Master if, elif, and else statements for decision making.", "duration": 25},
                    {"title": "Loops in Python", "content": "Learn for loops and while loops for iteration.", "duration": 30},
                    {"title": "Functions", "content": "Create reusable code with functions and parameters.", "duration": 35},
                ]
            }
        ]
    },
    {
        "title": "Data Science with Python",
        "description": "Master data analysis, visualization, and machine learning with Python.",
        "track_type": "Data Science",
        "level": "intermediate",
        "modules": [
            {
                "title": "Data Analysis with Pandas",
                "lessons": [
                    {"title": "Introduction to Pandas", "content": "Learn the basics of the Pandas library for data manipulation.", "duration": 30},
                    {"title": "DataFrames and Series", "content": "Understand core data structures in Pandas.", "duration": 35},
                    {"title": "Data Cleaning", "content": "Handle missing data, duplicates, and data transformation.", "duration": 40},
                ]
            },
            {
                "title": "Data Visualization",
                "lessons": [
                    {"title": "Matplotlib Basics", "content": "Create basic plots and charts with Matplotlib.", "duration": 30},
                    {"title": "Seaborn for Statistical Plots", "content": "Build beautiful statistical visualizations.", "duration": 35},
                    {"title": "Interactive Visualizations", "content": "Create interactive charts with Plotly.", "duration": 40},
                ]
            },
            {
                "title": "Introduction to Machine Learning",
                "lessons": [
                    {"title": "ML Fundamentals", "content": "Understand supervised vs unsupervised learning.", "duration": 35},
                    {"title": "Scikit-learn Basics", "content": "Build your first ML model with scikit-learn.", "duration": 45},
                    {"title": "Model Evaluation", "content": "Evaluate and improve your models.", "duration": 40},
                ]
            }
        ]
    },
    {
        "title": "Web Development with React",
        "description": "Build modern web applications with React.js and related technologies.",
        "track_type": "Engineering",
        "level": "intermediate",
        "modules": [
            {
                "title": "React Fundamentals",
                "lessons": [
                    {"title": "Introduction to React", "content": "Understand React's component-based architecture.", "duration": 25},
                    {"title": "JSX and Components", "content": "Learn JSX syntax and create functional components.", "duration": 30},
                    {"title": "Props and State", "content": "Manage data flow with props and component state.", "duration": 35},
                ]
            },
            {
                "title": "React Hooks",
                "lessons": [
                    {"title": "useState Hook", "content": "Manage state in functional components.", "duration": 30},
                    {"title": "useEffect Hook", "content": "Handle side effects and lifecycle events.", "duration": 35},
                    {"title": "Custom Hooks", "content": "Create reusable custom hooks.", "duration": 40},
                ]
            },
            {
                "title": "State Management",
                "lessons": [
                    {"title": "Context API", "content": "Share state across components without prop drilling.", "duration": 35},
                    {"title": "Redux Basics", "content": "Manage complex application state with Redux.", "duration": 45},
                    {"title": "React Query", "content": "Handle server state and caching.", "duration": 40},
                ]
            }
        ]
    },
    {
        "title": "UI/UX Design Principles",
        "description": "Learn the fundamentals of user interface and user experience design.",
        "track_type": "Design",
        "level": "beginner",
        "modules": [
            {
                "title": "Design Fundamentals",
                "lessons": [
                    {"title": "Color Theory", "content": "Understand color psychology and color palettes.", "duration": 25},
                    {"title": "Typography Basics", "content": "Learn font pairing and typography hierarchy.", "duration": 30},
                    {"title": "Layout and Composition", "content": "Master visual hierarchy and layout principles.", "duration": 35},
                ]
            },
            {
                "title": "User Experience Design",
                "lessons": [
                    {"title": "User Research", "content": "Conduct effective user research and interviews.", "duration": 40},
                    {"title": "Wireframing", "content": "Create low-fidelity wireframes for rapid prototyping.", "duration": 35},
                    {"title": "Usability Testing", "content": "Test and iterate on your designs.", "duration": 40},
                ]
            }
        ]
    },
    {
        "title": "Product Management Essentials",
        "description": "Learn how to build and manage successful products from ideation to launch.",
        "track_type": "Product Management",
        "level": "beginner",
        "modules": [
            {
                "title": "Product Strategy",
                "lessons": [
                    {"title": "Product Vision", "content": "Define clear product vision and strategy.", "duration": 30},
                    {"title": "Market Research", "content": "Analyze market trends and competition.", "duration": 35},
                    {"title": "Product Roadmap", "content": "Create and maintain product roadmaps.", "duration": 40},
                ]
            },
            {
                "title": "Agile Product Management",
                "lessons": [
                    {"title": "Scrum Framework", "content": "Understand Scrum roles, events, and artifacts.", "duration": 35},
                    {"title": "User Stories", "content": "Write effective user stories and acceptance criteria.", "duration": 30},
                    {"title": "Sprint Planning", "content": "Plan and execute successful sprints.", "duration": 35},
                ]
            }
        ]
    },
    {
        "title": "Business Analytics Fundamentals",
        "description": "Master data-driven decision making for business success.",
        "track_type": "Business Analytics",
        "level": "beginner",
        "modules": [
            {
                "title": "Excel for Analytics",
                "lessons": [
                    {"title": "Advanced Excel Functions", "content": "Master VLOOKUP, INDEX-MATCH, and pivot tables.", "duration": 35},
                    {"title": "Data Analysis in Excel", "content": "Perform statistical analysis in Excel.", "duration": 40},
                    {"title": "Excel Dashboards", "content": "Create interactive dashboards.", "duration": 45},
                ]
            },
            {
                "title": "SQL for Business",
                "lessons": [
                    {"title": "SQL Basics", "content": "Learn SELECT, WHERE, and JOIN operations.", "duration": 30},
                    {"title": "Advanced Queries", "content": "Subqueries, CTEs, and window functions.", "duration": 40},
                    {"title": "Database Design", "content": "Understand normalization and ERD.", "duration": 35},
                ]
            }
        ]
    },
    {
        "title": "Machine Learning Engineering",
        "description": "Build production-ready machine learning systems.",
        "track_type": "Data Science",
        "level": "advanced",
        "modules": [
            {
                "title": "ML Pipeline Design",
                "lessons": [
                    {"title": "Feature Engineering", "content": "Create meaningful features for ML models.", "duration": 45},
                    {"title": "Model Selection", "content": "Choose the right algorithm for your problem.", "duration": 40},
                    {"title": "Hyperparameter Tuning", "content": "Optimize model performance.", "duration": 50},
                ]
            },
            {
                "title": "Deep Learning",
                "lessons": [
                    {"title": "Neural Networks", "content": "Understand neural network architecture.", "duration": 50},
                    {"title": "TensorFlow Basics", "content": "Build models with TensorFlow.", "duration": 55},
                    {"title": "PyTorch Fundamentals", "content": "Deep learning with PyTorch.", "duration": 55},
                ]
            }
        ]
    },
    {
        "title": "Full-Stack JavaScript",
        "description": "Build complete web applications with Node.js and React.",
        "track_type": "Engineering",
        "level": "advanced",
        "modules": [
            {
                "title": "Node.js Backend",
                "lessons": [
                    {"title": "Express.js Setup", "content": "Create REST APIs with Express.", "duration": 40},
                    {"title": "MongoDB Integration", "content": "Connect and query MongoDB.", "duration": 45},
                    {"title": "Authentication", "content": "Implement JWT authentication.", "duration": 50},
                ]
            },
            {
                "title": "Full-Stack Integration",
                "lessons": [
                    {"title": "API Design", "content": "Design RESTful and GraphQL APIs.", "duration": 45},
                    {"title": "Deployment", "content": "Deploy to cloud platforms.", "duration": 40},
                    {"title": "DevOps Basics", "content": "CI/CD and containerization.", "duration": 50},
                ]
            }
        ]
    },
    {
        "title": "Mobile App Design",
        "description": "Design beautiful and intuitive mobile applications.",
        "track_type": "Design",
        "level": "intermediate",
        "modules": [
            {
                "title": "Mobile Design Patterns",
                "lessons": [
                    {"title": "iOS vs Android", "content": "Understand platform differences.", "duration": 30},
                    {"title": "Navigation Patterns", "content": "Design intuitive navigation.", "duration": 35},
                    {"title": "Gestures and Interactions", "content": "Mobile-specific interactions.", "duration": 40},
                ]
            }
        ]
    },
    {
        "title": "Data Engineering",
        "description": "Build robust data pipelines and infrastructure.",
        "track_type": "Data Science",
        "level": "advanced",
        "modules": [
            {
                "title": "ETL Pipelines",
                "lessons": [
                    {"title": "Apache Spark", "content": "Distributed data processing.", "duration": 50},
                    {"title": "Airflow", "content": "Orchestrate data workflows.", "duration": 45},
                    {"title": "Data Warehousing", "content": "Design data warehouse solutions.", "duration": 55},
                ]
            }
        ]
    },
    {
        "title": "Agile Methodology",
        "description": "Master Agile project management methodologies.",
        "track_type": "Product Management",
        "level": "intermediate",
        "modules": [
            {
                "title": "Scrum Deep Dive",
                "lessons": [
                    {"title": "Scrum Master Role", "content": "Lead effective Scrum teams.", "duration": 40},
                    {"title": "Retrospectives", "content": "Facilitate team improvement.", "duration": 35},
                    {"title": "Scaling Agile", "content": "SAFe and other frameworks.", "duration": 45},
                ]
            }
        ]
    },
    {
        "title": "Power BI Analytics",
        "description": "Create powerful business dashboards with Power BI.",
        "track_type": "Business Analytics",
        "level": "intermediate",
        "modules": [
            {
                "title": "Power BI Fundamentals",
                "lessons": [
                    {"title": "Data Modeling", "content": "Create relationships and measures.", "duration": 40},
                    {"title": "DAX Formulas", "content": "Write powerful DAX calculations.", "duration": 45},
                    {"title": "Report Design", "content": "Build interactive reports.", "duration": 40},
                ]
            }
        ]
    },
    {
        "title": "Cloud Computing Basics",
        "description": "Learn AWS, Azure, and GCP fundamentals.",
        "track_type": "Engineering",
        "level": "beginner",
        "modules": [
            {
                "title": "Cloud Fundamentals",
                "lessons": [
                    {"title": "Cloud Concepts", "content": "IaaS, PaaS, SaaS explained.", "duration": 25},
                    {"title": "AWS Services", "content": "Core AWS services overview.", "duration": 35},
                    {"title": "Cloud Security", "content": "Security best practices.", "duration": 30},
                ]
            }
        ]
    },
    {
        "title": "Design Systems",
        "description": "Create and maintain scalable design systems.",
        "track_type": "Design",
        "level": "advanced",
        "modules": [
            {
                "title": "Building Design Systems",
                "lessons": [
                    {"title": "Component Libraries", "content": "Create reusable components.", "duration": 45},
                    {"title": "Documentation", "content": "Write effective design docs.", "duration": 35},
                    {"title": "Figma Advanced", "content": "Advanced Figma techniques.", "duration": 50},
                ]
            }
        ]
    },
    {
        "title": "Product Analytics",
        "description": "Measure and optimize product performance.",
        "track_type": "Product Management",
        "level": "advanced",
        "modules": [
            {
                "title": "Analytics Strategy",
                "lessons": [
                    {"title": "KPIs and Metrics", "content": "Define meaningful metrics.", "duration": 35},
                    {"title": "A/B Testing", "content": "Design and analyze experiments.", "duration": 45},
                    {"title": "User Segmentation", "content": "Understand user cohorts.", "duration": 40},
                ]
            }
        ]
    }
]

# ============================================================================
# BADGE DATA
# ============================================================================
BADGES_DATA = [
    {"name": "First Steps", "description": "Complete your first lesson", "condition_type": BadgeConditionType.FIRST_LESSON, "color": "primary", "points": 10},
    {"name": "Course Champion", "description": "Complete an entire course", "condition_type": BadgeConditionType.COMPLETE_COURSE, "color": "success", "points": 100},
    {"name": "Quiz Master", "description": "Score 100% on 5 quizzes", "condition_type": BadgeConditionType.QUIZ_MASTER, "color": "warning", "points": 50},
    {"name": "Streak Star", "description": "Maintain a 7-day learning streak", "condition_type": BadgeConditionType.LEARNING_STREAK, "color": "secondary", "points": 75},
    {"name": "Perfect Attendance", "description": "100% attendance for a month", "condition_type": BadgeConditionType.ATTENDANCE_PERFECT, "color": "success", "points": 80},
    {"name": "High Achiever", "description": "Score above 90% on all quizzes in a module", "condition_type": BadgeConditionType.HIGH_SCORE, "color": "warning", "points": 60},
    {"name": "Module Master", "description": "Complete all lessons in a module", "condition_type": BadgeConditionType.MODULE_COMPLETION, "color": "primary", "points": 40},
    {"name": "Practice Champion", "description": "Complete 20 practice exercises", "condition_type": BadgeConditionType.PRACTICE_DEDICATION, "color": "secondary", "points": 50},
]

# ============================================================================
# QUIZ DATA (sample questions per lesson)
# ============================================================================
QUIZ_TEMPLATES = [
    {
        "question": "What is the primary purpose of {topic}?",
        "options": ["To organize data", "To improve performance", "Both A and B", "None of the above"],
        "correct": AnswerChoice.C
    },
    {
        "question": "Which of the following is true about {topic}?",
        "options": ["It is optional", "It is mandatory", "It depends on context", "It is deprecated"],
        "correct": AnswerChoice.C
    },
    {
        "question": "What is the best practice when using {topic}?",
        "options": ["Use sparingly", "Use frequently", "Follow documentation", "Avoid completely"],
        "correct": AnswerChoice.C
    },
]


def generate_email(name):
    """Generate email from name"""
    parts = name.lower().replace(" ", ".")
    return f"{parts}@student.elevated.com"


def generate_phone():
    """Generate random phone number"""
    return f"9{''.join([str(random.randint(0, 9)) for _ in range(9)])}"


def clear_database():
    """Clear all data from the database"""
    db = SessionLocal()
    try:
        print("Clearing existing data...")
        # Delete in reverse order of dependencies
        db.query(StudentBadge).delete()
        db.query(Badge).delete()
        db.query(QuizSubmission).delete()
        db.query(Quiz).delete()
        db.query(LessonProgress).delete()
        db.query(Enrollment).delete()
        db.query(Lesson).delete()
        db.query(Module).delete()
        db.query(Course).delete()
        db.query(Attendance).delete()
        db.query(WeeklySkillScore).delete()
        db.query(Student).delete()
        db.query(User).delete()
        db.commit()
        print("✓ Database cleared successfully!")
    except Exception as e:
        db.rollback()
        print(f"✗ Error clearing database: {str(e)}")
        raise
    finally:
        db.close()


def seed_database(reset=False):
    """Seed the database with comprehensive sample data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_students = db.query(Student).count()
        if existing_students > 0:
            if reset:
                db.close()
                clear_database()
                db = SessionLocal()
            else:
                print(f"Database already contains {existing_students} students.")
                print("Run with --reset flag to clear and reseed: python seed_db.py --reset")
                return
        
        # ====================================================================
        # 1. CREATE ADMIN AND MENTOR USERS
        # ====================================================================
        print("Creating admin and mentor users...")
        
        admin_user = User(
            email="admin@elevated.com",
            full_name="Admin",
            hashed_password=hash_password("dharsini@3137"),
            role="admin"
        )
        
        mentor_user = User(
            email="mentor@elevated.com",
            full_name="John Mentor",
            hashed_password=hash_password("mentor123"),
            role="mentor"
        )
        
        db.add(admin_user)
        db.add(mentor_user)
        db.flush()
        
        # ====================================================================
        # 2. CREATE STUDENT USERS AND STUDENTS (50+ students)
        # ====================================================================
        print(f"Creating {len(STUDENT_NAMES)} students with user accounts...")
        
        students = []
        student_users = []
        
        for name in STUDENT_NAMES:
            # Create user account for student
            email = generate_email(name)
            student_user = User(
                email=email,
                full_name=name,
                hashed_password=hash_password("student123"),  # Default password
                role="student"
            )
            student_users.append(student_user)
            db.add(student_user)
        
        db.flush()  # Get user IDs
        
        # Create student records
        for i, name in enumerate(STUDENT_NAMES):
            student = Student(
                name=name,
                age=random.randint(18, 28),
                guardian_contact=generate_phone(),
                interest_track=random.choice(TRACKS),
                predicted_track=random.choice(TRACKS)
            )
            students.append(student)
            db.add(student)
        
        db.flush()  # Get student IDs
        
        # ====================================================================
        # 3. CREATE COURSES, MODULES, AND LESSONS
        # ====================================================================
        print(f"Creating {len(COURSES_DATA)} courses with modules and lessons...")
        
        courses = []
        all_lessons = []
        
        for course_data in COURSES_DATA:
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                track_type=course_data["track_type"],
                level=course_data["level"]
            )
            db.add(course)
            db.flush()
            courses.append(course)
            
            # Create modules
            for module_order, module_data in enumerate(course_data["modules"], 1):
                module = Module(
                    course_id=course.id,
                    title=module_data["title"],
                    order_number=module_order
                )
                db.add(module)
                db.flush()
                
                # Create lessons
                for lesson_order, lesson_data in enumerate(module_data["lessons"], 1):
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_data["title"],
                        content=lesson_data["content"],
                        video_url=f"https://youtube.com/watch?v=sample{lesson_order}",
                        duration_minutes=lesson_data["duration"]
                    )
                    db.add(lesson)
                    db.flush()
                    all_lessons.append(lesson)
                    
                    # Create quiz for each lesson
                    quiz_template = random.choice(QUIZ_TEMPLATES)
                    quiz = Quiz(
                        lesson_id=lesson.id,
                        question=quiz_template["question"].format(topic=lesson_data["title"]),
                        option_a=quiz_template["options"][0],
                        option_b=quiz_template["options"][1],
                        option_c=quiz_template["options"][2],
                        option_d=quiz_template["options"][3],
                        correct_answer=quiz_template["correct"]
                    )
                    db.add(quiz)
        
        db.flush()
        
        # ====================================================================
        # 4. CREATE BADGES
        # ====================================================================
        print("Creating badges...")
        
        badges = []
        for badge_data in BADGES_DATA:
            badge = Badge(
                name=badge_data["name"],
                description=badge_data["description"],
                condition_type=badge_data["condition_type"],
                color=badge_data["color"],
                points=badge_data["points"],
                icon_url=f"/badges/{badge_data['name'].lower().replace(' ', '_')}.png"
            )
            db.add(badge)
            badges.append(badge)
        
        db.flush()
        
        # ====================================================================
        # 5. CREATE ENROLLMENTS
        # ====================================================================
        print("Creating student enrollments...")
        
        enrollments = []
        for student in students:
            # Each student enrolls in 2-4 courses
            num_courses = random.randint(2, 4)
            enrolled_courses = random.sample(courses, min(num_courses, len(courses)))
            
            for course in enrolled_courses:
                progress = random.randint(0, 100)
                enrollment = Enrollment(
                    student_id=student.id,
                    course_id=course.id,
                    progress_percentage=progress,
                    completed=progress == 100
                )
                enrollments.append(enrollment)
                db.add(enrollment)
        
        db.flush()
        
        # ====================================================================
        # 6. CREATE WEEKLY SKILL SCORES
        # ====================================================================
        print("Creating weekly skill scores...")
        
        base_date = datetime.now()
        
        for student in students:
            for week in range(12):
                week_ending = base_date - timedelta(weeks=week)
                
                quiz_score = random.uniform(70, 95)
                project_score = random.uniform(75, 98)
                attendance_score = random.uniform(80, 100)
                mentor_rating = random.uniform(70, 95)
                
                skill_score = round(
                    (quiz_score * 0.4) +
                    (project_score * 0.3) +
                    (attendance_score * 0.2) +
                    (mentor_rating * 0.1),
                    2
                )
                
                weekly_score = WeeklySkillScore(
                    student_id=student.id,
                    quiz_score=round(quiz_score, 2),
                    project_score=round(project_score, 2),
                    attendance_score=round(attendance_score, 2),
                    mentor_rating=round(mentor_rating, 2),
                    skill_score=skill_score,
                    week_ending=week_ending
                )
                db.add(weekly_score)
        
        # ====================================================================
        # 7. CREATE ATTENDANCE RECORDS
        # ====================================================================
        print("Creating attendance records (35 days)...")
        
        base_date_attendance = date.today()
        
        for student in students:
            for day_offset in range(35):
                attendance_date = base_date_attendance - timedelta(days=day_offset)
                present = random.choices([True, False], weights=[85, 15])[0]
                
                attendance_record = Attendance(
                    student_id=student.id,
                    date=attendance_date,
                    present=present
                )
                db.add(attendance_record)
        
        # ====================================================================
        # 8. CREATE STUDENT BADGES
        # ====================================================================
        print("Awarding badges to students...")
        
        for student in students:
            # Award 1-3 random badges to each student
            num_badges = random.randint(1, 3)
            awarded_badges = random.sample(badges, num_badges)
            
            for badge in awarded_badges:
                student_badge = StudentBadge(
                    student_id=student.id,
                    badge_id=badge.id,
                    earned_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    context_data=f"Earned for completing milestones"
                )
                db.add(student_badge)
        
        # ====================================================================
        # COMMIT ALL CHANGES
        # ====================================================================
        db.commit()
        
        print("\n" + "="*60)
        print("✓ DATABASE SEEDING COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"\n✓ Created 1 admin user")
        print(f"✓ Created 1 mentor user")
        print(f"✓ Created {len(STUDENT_NAMES)} students with user accounts")
        print(f"✓ Created {len(courses)} courses")
        print(f"✓ Created {len(all_lessons)} lessons with quizzes")
        print(f"✓ Created {len(badges)} badges")
        print(f"✓ Created {len(enrollments)} enrollments")
        print(f"✓ Created {len(STUDENT_NAMES) * 12} weekly skill scores")
        print(f"✓ Created {len(STUDENT_NAMES) * 35} attendance records")
        
        print("\n" + "-"*60)
        print("LOGIN CREDENTIALS:")
        print("-"*60)
        print("  ADMIN:")
        print("    Email:    admin@elevated.com")
        print("    Password: dharsini@3137")
        print("")
        print("  MENTOR:")
        print("    Email:    mentor@elevated.com")
        print("    Password: mentor123")
        print("")
        print("  STUDENTS (all use same password):")
        print("    Email:    [firstname.lastname]@student.elevated.com")
        print("    Password: student123")
        print("    Example:  aarav.patel@student.elevated.com")
        print("-"*60)
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    reset = "--reset" in sys.argv or "-r" in sys.argv
    if reset:
        print("Reset flag detected. Will clear existing data before seeding.\n")
    seed_database(reset=reset)
