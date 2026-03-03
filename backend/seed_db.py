"""
Database seeding script to populate the students and weekly skill scores tables
with sample data for development and testing.

Run this script from the backend directory with: python seed_db.py
"""

from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import Student, User, WeeklySkillScore, Attendance
from services.auth import hash_password
import random

# Sample data
STUDENT_NAMES = [
    "Aarav Patel", "Bhavna Sharma", "Chirag Verma", "Divya Gupta", "Eshan Kumar",
    "Fatima Khan", "Ganesh Singh", "Harsh Malhotra", "Ishita Reddy", "Jiya Kapoor",
    "Karan Nair", "Laxmi Rao", "Madhav Desai", "Neha Menon", "Omkar Tiwari",
    "Priya Saxena", "Quentin Das", "Ravi Sharma", "Sneha Pandey", "Tanvi Joshi"
]

TRACKS = ["Engineering", "Data Science", "Design", "Product Management", "Business Analytics"]

GUARDIAN_CONTACTS = [
    "9876543210", "8765432109", "7654321098", "6543210987", "5432109876",
    "4321098765", "3210987654", "2109876543", "1098765432", "9123456789",
    "8123456789", "7123456789", "6123456789", "5123456789", "4123456789",
    "3123456789", "2123456789", "1123456789", "9023456789", "8023456789"
]


def seed_database():
    """Seed the database with sample data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if students already exist to avoid duplicates
        existing_students = db.query(Student).count()
        if existing_students > 0:
            print(f"Database already contains {existing_students} students. Skipping seeding.")
            return
        
        # Create sample users (mentors and admin)
        print("Creating sample users...")
        admin_user = User(
            email="admin@elevated.com",
            full_name="Admin User",
            hashed_password=hash_password("admin123"),
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
        db.flush()  # Get IDs without committing yet
        
        # Create 20 students
        print("Creating 20 students...")
        students = []
        for i, name in enumerate(STUDENT_NAMES):
            student = Student(
                name=name,
                age=random.randint(18, 25),
                guardian_contact=GUARDIAN_CONTACTS[i],
                interest_track=random.choice(TRACKS),
                predicted_track=random.choice(TRACKS)
            )
            students.append(student)
            db.add(student)
        
        db.flush()  # Get student IDs
        
        # Create weekly skill scores for each student (past 12 weeks)
        print("Creating weekly skill scores for students...")
        base_date = datetime.now()
        
        for student in students:
            # Generate scores for the past 12 weeks
            for week in range(12):
                week_ending = base_date - timedelta(weeks=week)
                
                # Generate realistic scores
                quiz_score = random.uniform(70, 95)
                project_score = random.uniform(75, 98)
                attendance_score = random.uniform(80, 100)
                mentor_rating = random.uniform(70, 95)
                
                # Calculate skill score
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
        
        # Create attendance records for each student (past 35 days)
        print("Creating attendance records for students (35 days)...")
        base_date_attendance = date.today()
        
        for student in students:
            # Generate attendance for the past 35 days
            for day_offset in range(35):
                attendance_date = base_date_attendance - timedelta(days=day_offset)
                
                # Randomly assign presence (80% present, 20% absent)
                present = random.choices([True, False], weights=[80, 20])[0]
                
                attendance_record = Attendance(
                    student_id=student.id,
                    date=attendance_date,
                    present=present
                )
                db.add(attendance_record)
        
        # Commit all changes
        db.commit()
        print("✓ Database seeding completed successfully!")
        print(f"✓ Created {len(STUDENT_NAMES)} students")
        print(f"✓ Created {len(STUDENT_NAMES) * 12} weekly skill score records")
        print(f"✓ Created {len(STUDENT_NAMES) * 35} attendance records (35 days)")
        print("\nSample User Credentials:")
        print("  Admin: admin@elevated.com / admin123")
        print("  Mentor: mentor@elevated.com / mentor123")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error during seeding: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
