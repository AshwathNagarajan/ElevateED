"""
Reset the ElevateED database and load focused guidance-demo data.

This script is intentionally destructive. It drops all known application
tables, recreates the schema, and inserts a compact dataset that supports
student guidance, recommendations, dashboards, mentors, progress, quizzes,
attendance, and badges.

Run from the backend folder:
    python reset_guidance_demo_data.py
"""

from datetime import date, datetime, timedelta

from core.security import TokenManager
from database import Base, SessionLocal, engine
from models import (
    Attendance,
    Badge,
    Course,
    Enrollment,
    Lesson,
    LessonProgress,
    Mentor,
    Module,
    Quiz,
    QuizSubmission,
    RoleEnum,
    Student,
    StudentBadge,
    User,
    WeeklySkillScore,
)
from models.badge import BadgeConditionType
from models.quiz import AnswerChoice


DEMO_PASSWORDS = {
    "admin.guide@elevated.com": "Admin@123",
    "teacher.guide@elevated.com": "Teacher@123",
    "mentor.engineering@elevated.com": "Teacher@123",
    "mentor.business@elevated.com": "Teacher@123",
    "mentor.design@elevated.com": "Teacher@123",
    "student.guide@elevated.com": "Student@123",
    "ananya.cs@student.elevated.com": "Student@123",
    "rohan.business@student.elevated.com": "Student@123",
    "zoya.design@student.elevated.com": "Student@123",
    "vivaan.bio@student.elevated.com": "Student@123",
}


COURSES = [
    {
        "title": "Engineering Mathematics I: Calculus and Linear Algebra",
        "track_type": "Engineering",
        "level": "Advanced",
        "duration_hours": 32,
        "rating": 4.8,
        "mentor": "mentor.engineering@elevated.com",
        "description": "Notes-first coverage of limits, differentiation, matrices, eigenvalues, and first-semester problem patterns.",
        "modules": [
            ("Differential Calculus", ["Limits and continuity", "Derivative rules and rates", "Taylor approximation notes"]),
            ("Matrix Algebra", ["Matrix operations", "Rank and inverse", "Eigenvalues and eigenvectors"]),
            ("Applied Problem Sets", ["Optimization models", "Linear systems practice", "Exam-style mixed problems"]),
        ],
    },
    {
        "title": "Programming Fundamentals: C and Python Logic",
        "track_type": "Computer Science",
        "level": "Advanced",
        "duration_hours": 30,
        "rating": 4.9,
        "mentor": "teacher.guide@elevated.com",
        "description": "Structured notes on variables, control flow, arrays, functions, recursion, and algorithmic thinking.",
        "modules": [
            ("Core Syntax and Flow", ["Variables and types", "Conditionals and loops", "Tracing dry runs"]),
            ("Functions and Memory", ["Function decomposition", "Arrays and strings", "Pointers as memory notes"]),
            ("Algorithm Patterns", ["Searching and sorting basics", "Recursion fundamentals", "Complexity intuition"]),
        ],
    },
    {
        "title": "Data Science Foundations: Statistics and Python",
        "track_type": "Data Science",
        "level": "Advanced",
        "duration_hours": 34,
        "rating": 4.8,
        "mentor": "teacher.guide@elevated.com",
        "description": "First-semester notes for descriptive statistics, probability, Python data handling, and interpretation.",
        "modules": [
            ("Statistics Notes", ["Mean variance and spread", "Probability rules", "Distributions and sampling"]),
            ("Python Data Work", ["Lists dictionaries and files", "Numpy array thinking", "Pandas table operations"]),
            ("Interpreting Data", ["Correlation versus causation", "Outlier checks", "Mini analysis report"]),
        ],
    },
    {
        "title": "Business Analytics I: Spreadsheets, Metrics, and Decisions",
        "track_type": "Business Analytics",
        "level": "Advanced",
        "duration_hours": 28,
        "rating": 4.7,
        "mentor": "mentor.business@elevated.com",
        "description": "Notes on business metrics, spreadsheet models, charts, forecasting, and decision reasoning.",
        "modules": [
            ("Business Metrics", ["Revenue cost and margin", "Growth and retention", "KPI quality checks"]),
            ("Spreadsheet Modelling", ["Formulas and references", "Lookup and pivot notes", "Scenario tables"]),
            ("Decision Analytics", ["Forecasting basics", "Chart selection", "Recommendation writing"]),
        ],
    },
    {
        "title": "Design Studio I: Visual Thinking and UX Basics",
        "track_type": "Design",
        "level": "Advanced",
        "duration_hours": 26,
        "rating": 4.8,
        "mentor": "mentor.design@elevated.com",
        "description": "Studio-style notes on visual hierarchy, typography, user flows, and critique-ready design decisions.",
        "modules": [
            ("Visual Foundations", ["Gestalt principles", "Typography scale", "Color and contrast"]),
            ("UX Thinking", ["User goals and pain points", "Information architecture", "Wireframe notes"]),
            ("Studio Practice", ["Critique checklist", "Prototype decisions", "Portfolio case notes"]),
        ],
    },
    {
        "title": "Professional Communication and Technical Writing",
        "track_type": "Humanities",
        "level": "Advanced",
        "duration_hours": 24,
        "rating": 4.7,
        "mentor": "mentor.design@elevated.com",
        "description": "First-semester notes for academic reading, technical summaries, presentations, and professional email.",
        "modules": [
            ("Academic Reading", ["Skimming and scanning", "Argument mapping", "Source credibility"]),
            ("Technical Writing", ["Definition and process notes", "Report structure", "Editing for clarity"]),
            ("Speaking and Presentation", ["Audience analysis", "Slide story flow", "Q and A preparation"]),
        ],
    },
    {
        "title": "Life Science I: Cell Biology and Biomolecules",
        "track_type": "Life Science",
        "level": "Advanced",
        "duration_hours": 30,
        "rating": 4.6,
        "mentor": "mentor.engineering@elevated.com",
        "description": "Notes-first introduction to cell structure, membranes, biomolecules, enzymes, and lab reasoning.",
        "modules": [
            ("Cell Structure", ["Cell organelles", "Membrane transport", "Microscopy notes"]),
            ("Biomolecules", ["Carbohydrates and lipids", "Proteins and enzymes", "Nucleic acid basics"]),
            ("Lab Reasoning", ["Observation tables", "Controls and variables", "Result interpretation"]),
        ],
    },
    {
        "title": "Financial Accounting I: Journal to Trial Balance",
        "track_type": "Commerce",
        "level": "Advanced",
        "duration_hours": 27,
        "rating": 4.7,
        "mentor": "mentor.business@elevated.com",
        "description": "First-semester notes for accounting equation, journal entries, ledgers, trial balance, and error checks.",
        "modules": [
            ("Accounting Foundations", ["Accounting equation", "Debit and credit rules", "Source documents"]),
            ("Books of Accounts", ["Journal entries", "Ledger posting", "Cash book notes"]),
            ("Trial Balance", ["Balancing accounts", "Error detection", "Adjustment thinking"]),
        ],
    },
]


STUDENTS = [
    {
        "email": "student.guide@elevated.com",
        "name": "Demo Student Guide",
        "age": 18,
        "guardian": "+91-90000-10001",
        "interest": "Computer Science",
        "predicted": "Computer Science",
        "courses": [("Programming Fundamentals: C and Python Logic", 38), ("Engineering Mathematics I: Calculus and Linear Algebra", 24)],
        "quiz_pattern": [True, False, True, False, True, False],
        "attendance": [True, True, False, True, True, True, False, True],
        "skill_scores": [58, 61, 64, 66],
    },
    {
        "email": "ananya.cs@student.elevated.com",
        "name": "Ananya Iyer",
        "age": 18,
        "guardian": "+91-90000-10002",
        "interest": "Data Science",
        "predicted": "Data Science",
        "courses": [("Data Science Foundations: Statistics and Python", 68), ("Programming Fundamentals: C and Python Logic", 44)],
        "quiz_pattern": [True, True, False, True, True, True],
        "attendance": [True, True, True, True, False, True, True, True],
        "skill_scores": [66, 70, 73, 76],
    },
    {
        "email": "rohan.business@student.elevated.com",
        "name": "Rohan Mehta",
        "age": 19,
        "guardian": "+91-90000-10003",
        "interest": "Business Analytics",
        "predicted": "Business Analytics",
        "courses": [("Business Analytics I: Spreadsheets, Metrics, and Decisions", 52), ("Financial Accounting I: Journal to Trial Balance", 31)],
        "quiz_pattern": [False, True, False, True, False, True],
        "attendance": [True, False, True, True, False, True, True, False],
        "skill_scores": [52, 55, 57, 60],
    },
    {
        "email": "zoya.design@student.elevated.com",
        "name": "Zoya Khan",
        "age": 18,
        "guardian": "+91-90000-10004",
        "interest": "Design",
        "predicted": "Design",
        "courses": [("Design Studio I: Visual Thinking and UX Basics", 74), ("Professional Communication and Technical Writing", 42)],
        "quiz_pattern": [True, True, True, False, True, True],
        "attendance": [True, True, True, True, True, True, True, True],
        "skill_scores": [72, 76, 80, 83],
    },
    {
        "email": "vivaan.bio@student.elevated.com",
        "name": "Vivaan Thomas",
        "age": 18,
        "guardian": "+91-90000-10005",
        "interest": "Life Science",
        "predicted": "Life Science",
        "courses": [("Life Science I: Cell Biology and Biomolecules", 57), ("Professional Communication and Technical Writing", 28)],
        "quiz_pattern": [True, False, True, True, False, True],
        "attendance": [True, True, True, False, True, True, True, False],
        "skill_scores": [60, 64, 68, 71],
    },
]


def make_user(email: str, full_name: str, role: RoleEnum) -> User:
    return User(
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=TokenManager.hash_password(DEMO_PASSWORDS[email]),
    )


def add_quiz_for_lesson(lesson: Lesson, track: str, order: int) -> Quiz:
    questions = {
        "Engineering": (
            "Which method is most reliable for checking a matrix inverse?",
            "Multiply the matrix by its inverse and confirm the identity matrix",
            "Check only the first row",
            "Compare the largest entries",
            "Ignore determinant conditions",
        ),
        "Computer Science": (
            "What does a dry run help you understand?",
            "How variable values change step by step",
            "Only the final output font",
            "The color of the editor",
            "Whether comments are long",
        ),
        "Data Science": (
            "Why should an outlier be inspected before removing it?",
            "It may be a valid signal or a data quality issue",
            "Outliers are always wrong",
            "Outliers never affect averages",
            "It makes charts colorful",
        ),
        "Business Analytics": (
            "What makes a KPI useful?",
            "It connects clearly to a decision or outcome",
            "It has the longest name",
            "It is impossible to measure",
            "It changes randomly",
        ),
        "Design": (
            "What is visual hierarchy used for?",
            "Guiding attention from most important to least important information",
            "Making every element identical",
            "Removing contrast",
            "Ignoring user goals",
        ),
        "Humanities": (
            "What improves a technical summary?",
            "Keeping the main claim, evidence, and result clear",
            "Adding unrelated stories",
            "Removing all structure",
            "Using only abbreviations",
        ),
        "Life Science": (
            "Why are controls used in lab work?",
            "To compare results against a stable reference",
            "To make observations unnecessary",
            "To change every variable",
            "To avoid recording data",
        ),
        "Commerce": (
            "What should total debits equal in a trial balance?",
            "Total credits",
            "Total assets only",
            "Net profit only",
            "The number of transactions",
        ),
    }
    question, correct, option_b, option_c, option_d = questions[track]
    return Quiz(
        lesson=lesson,
        question=f"{question} ({order})",
        option_a=correct,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_answer=AnswerChoice.A,
    )


def build_lesson_notes(course_data: dict, module_title: str, lesson_title: str, module_index: int, lesson_order: int) -> str:
    difficulty = ["Foundation", "Applied", "Challenge"][min(module_index - 1, 2)]
    examples = {
        "Engineering": "For a matrix problem, write the given matrix, state the operation, compute one row carefully, then verify the result with a reverse check.",
        "Computer Science": "For a program trace, create columns for each variable and update them line by line before deciding the final output.",
        "Data Science": "For a dataset, calculate one summary statistic, explain what it says, then mention one thing it cannot prove.",
        "Business Analytics": "For a business metric, define the numerator and denominator, calculate the value, then connect it to a decision.",
        "Design": "For a design critique, identify the user goal, name the hierarchy decision, and explain the tradeoff.",
        "Humanities": "For a paragraph or report, identify the claim, the evidence, and the audience before rewriting it.",
        "Life Science": "For a biology diagram, label the structure, explain its role, then connect it to a process.",
        "Commerce": "For an accounting entry, identify the affected accounts, apply debit-credit rules, then check the accounting equation.",
    }
    mistakes = {
        "Engineering": "Skipping verification, mixing row and column operations, or using a formula before checking conditions.",
        "Computer Science": "Guessing output without a dry run, ignoring data types, or changing more than one loop variable mentally.",
        "Data Science": "Treating correlation as proof, ignoring outliers, or reading an average without spread.",
        "Business Analytics": "Choosing a metric because it looks impressive instead of because it supports a decision.",
        "Design": "Decorating before solving the user problem or making every element compete for attention.",
        "Humanities": "Summarizing every detail instead of preserving the central argument and evidence.",
        "Life Science": "Memorizing names without linking structures to functions and experimental evidence.",
        "Commerce": "Posting to the wrong side of an account or forgetting that every transaction has two effects.",
    }
    challenge = {
        "Foundation": "Rewrite the definition in your own words and solve the simplest example.",
        "Applied": "Solve one mixed problem and explain why the selected method fits.",
        "Challenge": "Compare two similar problems, spot the trap, and write a short exam-ready answer.",
    }[difficulty]

    return (
        f"{difficulty} note: {lesson_title}\n\n"
        f"Course stream: {course_data['track_type']}\n"
        f"Module: {module_title}\n\n"
        "Learning goal:\n"
        f"Understand {lesson_title.lower()} well enough to solve a first-semester college problem without depending on video explanation.\n\n"
        "Core explanation:\n"
        f"This lesson starts from the key idea, then moves into a guided application. In {course_data['track_type']}, the important habit is to name what is given, "
        "choose the correct rule or framework, solve in visible steps, and check whether the result makes sense.\n\n"
        "Worked pattern:\n"
        f"{examples[course_data['track_type']]}\n\n"
        "Common mistake to avoid:\n"
        f"{mistakes[course_data['track_type']]}\n\n"
        "Practice ladder:\n"
        "1. Recall the definition or rule.\n"
        "2. Solve a direct example.\n"
        "3. Solve one changed example where a value, condition, or context is different.\n"
        f"4. {challenge}\n\n"
        "Reflection prompt:\n"
        "Before taking the quiz, write the one step that felt hardest. ElevateED treats that as a support signal and adjusts future guidance."
    )


def reset_schema() -> None:
    print("Dropping existing ElevateED tables...")
    Base.metadata.drop_all(bind=engine)
    print("Creating fresh ElevateED tables...")
    Base.metadata.create_all(bind=engine)


def seed_data() -> None:
    db = SessionLocal()
    try:
        users_by_email: dict[str, User] = {}

        admin = make_user("admin.guide@elevated.com", "ElevateED Admin", RoleEnum.ADMIN)
        db.add(admin)

        mentor_profiles = [
            (
                "teacher.guide@elevated.com",
                "Demo Teacher Guide",
                "M.Tech Computer Science",
                "Programming, data science, and adaptive learning",
                8,
                "Guides first-semester learners through notes, worked examples, and quiz-based feedback.",
            ),
            (
                "mentor.engineering@elevated.com",
                "Dr. Riya Sharma",
                "Ph.D. Applied Mathematics",
                "Engineering mathematics and life science reasoning",
                9,
                "Explains abstract first-semester topics through compact notes and practice ladders.",
            ),
            (
                "mentor.business@elevated.com",
                "Arjun Menon",
                "MBA Business Analytics",
                "Business analytics and accounting",
                7,
                "Connects metrics, spreadsheets, and accounting ideas to decision-making exercises.",
            ),
            (
                "mentor.design@elevated.com",
                "Anika Thomas",
                "M.Des Communication Design",
                "Design thinking and professional communication",
                6,
                "Helps learners build visual reasoning, critique habits, and clear technical communication.",
            ),
        ]

        for email, name, qualification, specialization, years, bio in mentor_profiles:
            user = make_user(email, name, RoleEnum.MENTOR)
            users_by_email[email] = user
            db.add(user)
            db.flush()
            db.add(
                Mentor(
                    user_id=user.id,
                    name=name,
                    phone="+91-90000-20000",
                    qualification=qualification,
                    specialization=specialization,
                    experience_years=years,
                    bio=bio,
                )
            )

        student_records: dict[str, Student] = {}
        student_users: dict[str, User] = {}
        for item in STUDENTS:
            user = make_user(item["email"], item["name"], RoleEnum.STUDENT)
            db.add(user)
            db.flush()
            student = Student(
                user_id=user.id,
                name=item["name"],
                age=item["age"],
                guardian_contact=item["guardian"],
                interest_track=item["interest"],
                predicted_track=item["predicted"],
            )
            db.add(student)
            student_users[item["email"]] = user
            student_records[item["email"]] = student

        db.flush()

        badges = [
            Badge(
                name="First Step",
                description="Completed the first lesson and started building a learning rhythm.",
                condition_type=BadgeConditionType.FIRST_LESSON,
                color="success",
                points=10,
            ),
            Badge(
                name="Steady Builder",
                description="Kept learning across multiple sessions in a week.",
                condition_type=BadgeConditionType.LEARNING_STREAK,
                color="primary",
                points=20,
            ),
            Badge(
                name="Quiz Climber",
                description="Improved quiz confidence through regular practice.",
                condition_type=BadgeConditionType.QUIZ_MASTER,
                color="warning",
                points=25,
            ),
            Badge(
                name="Focus Finisher",
                description="Completed a meaningful set of lessons in one course.",
                condition_type=BadgeConditionType.MODULE_COMPLETION,
                color="secondary",
                points=30,
            ),
        ]
        db.add_all(badges)
        db.flush()

        courses_by_title: dict[str, Course] = {}
        lessons_by_course: dict[str, list[Lesson]] = {}
        for course_data in COURSES:
            mentor = users_by_email[course_data["mentor"]]
            course = Course(
                title=course_data["title"],
                description=course_data["description"],
                track_type=course_data["track_type"],
                level=course_data["level"],
                duration_hours=course_data["duration_hours"],
                instructor=mentor.full_name,
                rating=course_data["rating"],
                mentor_id=mentor.id,
            )
            db.add(course)
            db.flush()

            course_lessons: list[Lesson] = []
            lesson_order = 1
            for module_index, (module_title, lesson_titles) in enumerate(course_data["modules"], start=1):
                module = Module(course_id=course.id, title=module_title, order_number=module_index)
                db.add(module)
                db.flush()
                for lesson_title in lesson_titles:
                    lesson = Lesson(
                        module_id=module.id,
                        title=lesson_title,
                        content=build_lesson_notes(course_data, module_title, lesson_title, module_index, lesson_order),
                        video_url=None,
                        duration_minutes=16 + (module_index * 4) + lesson_order,
                    )
                    db.add(lesson)
                    db.flush()
                    db.add(add_quiz_for_lesson(lesson, course_data["track_type"], lesson_order))
                    course_lessons.append(lesson)
                    lesson_order += 1

            courses_by_title[course.title] = course
            lessons_by_course[course.title] = course_lessons

        db.flush()

        today = date.today()
        now = datetime.utcnow()
        for item in STUDENTS:
            user = student_users[item["email"]]
            student = student_records[item["email"]]

            for course_title, progress in item["courses"]:
                course = courses_by_title[course_title]
                course_lessons = lessons_by_course[course_title]
                completed_lessons = max(1, round((progress / 100) * len(course_lessons)))
                db.add(
                    Enrollment(
                        student_id=user.id,
                        course_id=course.id,
                        progress_percentage=progress,
                        completed=progress >= 95,
                    )
                )
                for index, lesson in enumerate(course_lessons[:completed_lessons]):
                    db.add(
                        LessonProgress(
                            student_id=user.id,
                            lesson_id=lesson.id,
                            completed=True,
                            completion_date=now - timedelta(days=completed_lessons - index),
                        )
                    )

                for index, is_correct in enumerate(item["quiz_pattern"]):
                    lesson = course_lessons[index % len(course_lessons)]
                    quiz = lesson.quizzes[0]
                    db.add(
                        QuizSubmission(
                            student_id=student.id,
                            quiz_id=quiz.id,
                            selected_answer=AnswerChoice.A if is_correct else AnswerChoice.B,
                            score=100 if is_correct else 0,
                            is_correct=is_correct,
                            submitted_at=now - timedelta(days=len(item["quiz_pattern"]) - index),
                        )
                    )

            for day_offset, present in enumerate(item["attendance"]):
                db.add(
                    Attendance(
                        student_id=student.id,
                        date=today - timedelta(days=len(item["attendance"]) - day_offset),
                        present=present,
                    )
                )

            for week_index, skill_score in enumerate(item["skill_scores"], start=1):
                db.add(
                    WeeklySkillScore(
                        student_id=student.id,
                        quiz_score=max(45, skill_score - 3),
                        project_score=skill_score,
                        attendance_score=min(100, skill_score + 8),
                        mentor_rating=min(100, skill_score + 5),
                        skill_score=skill_score,
                        week_ending=now - timedelta(weeks=5 - week_index),
                    )
                )

            earned_count = 2 if item["skill_scores"][-1] < 70 else 3
            for badge in badges[:earned_count]:
                db.add(
                    StudentBadge(
                        student_id=student.id,
                        badge_id=badge.id,
                        context_data="Seeded guidance-demo achievement",
                    )
                )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def print_summary() -> None:
    db = SessionLocal()
    try:
        counts = {
            "users": db.query(User).count(),
            "students": db.query(Student).count(),
            "mentors": db.query(Mentor).count(),
            "courses": db.query(Course).count(),
            "modules": db.query(Module).count(),
            "lessons": db.query(Lesson).count(),
            "quizzes": db.query(Quiz).count(),
            "enrollments": db.query(Enrollment).count(),
            "quiz_submissions": db.query(QuizSubmission).count(),
            "attendance_records": db.query(Attendance).count(),
            "weekly_skill_scores": db.query(WeeklySkillScore).count(),
            "badges": db.query(Badge).count(),
        }
        print("\nFresh ElevateED guidance-demo data loaded:")
        for name, count in counts.items():
            print(f"  - {name}: {count}")
        print("\nDemo logins:")
        for email, password in DEMO_PASSWORDS.items():
            print(f"  - {email} / {password}")
    finally:
        db.close()


if __name__ == "__main__":
    reset_schema()
    seed_data()
    print_summary()
