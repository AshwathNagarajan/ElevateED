"""
Script to add attendance records for existing students for the last 35 days.
"""

from datetime import date, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Student, Attendance
import random


def add_attendance_records():
    """Add attendance records for all existing students for the past 35 days"""
    
    db = SessionLocal()
    
    try:
        # Get all students
        students = db.query(Student).all()
        
        if not students:
            print("No students found in database.")
            return
        
        # Check if attendance records already exist
        existing_attendance = db.query(Attendance).count()
        if existing_attendance > 0:
            print(f"Database already contains {existing_attendance} attendance records. Skipping.")
            return
        
        print(f"Adding attendance records for {len(students)} students (35 days)...")
        base_date = date.today()
        
        for student in students:
            # Generate attendance for the past 35 days
            for day_offset in range(35):
                attendance_date = base_date - timedelta(days=day_offset)
                
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
        print("✓ Attendance records added successfully!")
        print(f"✓ Created {len(students) * 35} attendance records ({len(students)} students × 35 days)")
        
    except Exception as e:
        db.rollback()
        print(f"✗ Error adding attendance records: {str(e)}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    add_attendance_records()
