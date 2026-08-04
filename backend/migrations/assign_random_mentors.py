"""
Migration script to assign random mentors to existing courses that don't have a mentor assigned.
Run this script once to assign mentors to existing courses.
"""
import sys
import os
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db, engine
from sqlalchemy.orm import Session
from models.course import Course
from models.mentor import Mentor


def assign_random_mentors():
    """Assign random mentors to courses that don't have one assigned."""
    db = Session(engine)
    
    try:
        # Get all mentors
        mentors = db.query(Mentor).all()
        
        if not mentors:
            print("No mentors found in database. Please seed mentors first.")
            return
        
        # Get mentor user_ids (which is what course.mentor_id references)
        mentor_user_ids = [mentor.user_id for mentor in mentors]
        print(f"Found {len(mentor_user_ids)} mentors: {mentor_user_ids}")
        
        # Get all courses without a mentor
        courses_without_mentor = db.query(Course).filter(Course.mentor_id == None).all()
        
        if not courses_without_mentor:
            print("All courses already have mentors assigned.")
            return
        
        print(f"Found {len(courses_without_mentor)} courses without mentors.")
        
        # Assign random mentors to each course
        assigned_count = 0
        for course in courses_without_mentor:
            # Pick a random mentor
            random_mentor_user_id = random.choice(mentor_user_ids)
            
            # Assign mentor to course
            course.mentor_id = random_mentor_user_id
            assigned_count += 1
            
            # Get mentor name for logging
            mentor = next(m for m in mentors if m.user_id == random_mentor_user_id)
            print(f"  Assigned '{mentor.name}' (user_id: {random_mentor_user_id}) to '{course.title}'")
        
        # Commit changes
        db.commit()
        print(f"\nSuccessfully assigned mentors to {assigned_count} courses.")
        
    except Exception as e:
        db.rollback()
        print(f"Error assigning mentors: {e}")
        raise
    finally:
        db.close()


def show_course_mentor_assignments():
    """Display current course-mentor assignments."""
    db = Session(engine)
    
    try:
        courses = db.query(Course).all()
        mentors = {m.user_id: m for m in db.query(Mentor).all()}
        
        print("\nCurrent Course-Mentor Assignments:")
        print("-" * 70)
        
        for course in courses:
            if course.mentor_id and course.mentor_id in mentors:
                mentor = mentors[course.mentor_id]
                print(f"  {course.title[:40]:<42} => {mentor.name}")
            else:
                print(f"  {course.title[:40]:<42} => (No mentor)")
        
        print("-" * 70)
        
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 70)
    print("Assigning Random Mentors to Courses")
    print("=" * 70)
    
    assign_random_mentors()
    show_course_mentor_assignments()
