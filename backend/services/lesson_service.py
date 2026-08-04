"""
Lesson service for handling lesson progress and course progress calculations.
Provides clean interfaces for lesson operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import LessonProgress, Lesson, Module, Enrollment, Course
from datetime import datetime
from typing import Optional, Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# LESSON PROGRESS
# ============================================================================

def mark_lesson_complete(
    student_id: int,
    lesson_id: int,
    db: Session
) -> Optional[LessonProgress]:
    """
    Mark a lesson as complete for a student.
    
    Args:
        student_id: ID of the student (user_id)
        lesson_id: ID of the lesson
        db: Database session
        
    Returns:
        Updated LessonProgress or None if lesson not found
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        logger.warning(f"Lesson {lesson_id} not found")
        return None
    
    # Get or create lesson progress
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not lesson_progress:
        # Create new lesson progress entry
        lesson_progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            completed=True,
            completion_date=datetime.utcnow()
        )
        db.add(lesson_progress)
        logger.info(f"Created lesson progress for student {student_id}, lesson {lesson_id}")
    else:
        # Update existing entry
        if not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.completion_date = datetime.utcnow()
            logger.info(f"Updated lesson progress for student {student_id}, lesson {lesson_id}")
        else:
            # Already completed - return existing (idempotent)
            return lesson_progress
    
    db.commit()
    db.refresh(lesson_progress)
    
    return lesson_progress


def start_lesson(
    student_id: int,
    lesson_id: int,
    db: Session
) -> Optional[LessonProgress]:
    """
    Mark the start of a lesson for a student.
    
    Creates a LessonProgress entry if one doesn't exist.
    
    Args:
        student_id: ID of the student
        lesson_id: ID of the lesson
        db: Database session
        
    Returns:
        LessonProgress record or None if lesson not found
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        return None
    
    # Get or create progress
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not lesson_progress:
        lesson_progress = LessonProgress(
            student_id=student_id,
            lesson_id=lesson_id,
            completed=False,
            started_at=datetime.utcnow()
        )
        db.add(lesson_progress)
        db.commit()
        db.refresh(lesson_progress)
    
    return lesson_progress


def get_lesson_progress(
    student_id: int,
    lesson_id: int,
    db: Session
) -> Optional[LessonProgress]:
    """
    Get a student's progress on a specific lesson.
    
    Args:
        student_id: ID of the student
        lesson_id: ID of the lesson
        db: Database session
        
    Returns:
        LessonProgress or None if not found
    """
    return db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()


# ============================================================================
# COURSE PROGRESS CALCULATION
# ============================================================================

def calculate_course_progress(
    student_id: int,
    course_id: int,
    db: Session
) -> float:
    """
    Calculate the overall progress percentage for a course.
    
    Progress = (completed lessons / total lessons) * 100
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        db: Database session
        
    Returns:
        Progress percentage (0-100)
    """
    try:
        # Get total lessons in course
        total_lessons = db.query(func.count(Lesson.id)).join(
            Module, Module.id == Lesson.module_id
        ).filter(Module.course_id == course_id).scalar() or 0
        
        if total_lessons == 0:
            return 0.0
        
        # Get completed lessons for student
        completed_lessons = db.query(func.count(LessonProgress.id)).filter(
            and_(
                LessonProgress.student_id == student_id,
                LessonProgress.completed == True,
                LessonProgress.lesson_id.in_(
                    db.query(Lesson.id).join(
                        Module, Module.id == Lesson.module_id
                    ).filter(Module.course_id == course_id)
                )
            )
        ).scalar() or 0
        
        progress = (completed_lessons / total_lessons) * 100
        return min(progress, 100.0)
    except Exception as e:
        logger.error(f"Error calculating course progress: {str(e)}")
        return 0.0


# ============================================================================
# ENROLLMENT PROGRESS UPDATE
# ============================================================================

def update_course_progress(
    student_id: int,
    course_id: int,
    db: Session
) -> bool:
    """
    Calculate and update the enrollment progress for a course.
    
    Also marks enrollment as completed if all lessons are done.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        db: Database session
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Find enrollment
        enrollment = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id
            )
        ).first()
        
        if not enrollment:
            logger.warning(f"Enrollment not found for student {student_id}, course {course_id}")
            return False
        
        # Calculate progress
        progress = calculate_course_progress(student_id, course_id, db)
        
        # Update enrollment
        enrollment.progress_percentage = progress
        
        # Mark as completed if all lessons are done
        if progress >= 100.0:
            enrollment.completed = True
        
        db.commit()
        db.refresh(enrollment)
        
        logger.info(f"Updated course progress for student {student_id}, course {course_id}: {progress}%")
        return True
    except Exception as e:
        logger.error(f"Error updating course progress: {str(e)}")
        return False


# ============================================================================
# COURSE COMPLETION CHECK
# ============================================================================

def is_course_completed(
    student_id: int,
    course_id: int,
    db: Session
) -> bool:
    """
    Check if a student has completed all lessons in a course.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        db: Database session
        
    Returns:
        True if all lessons completed, False otherwise
    """
    try:
        # Get total lessons
        total_lessons = db.query(func.count(Lesson.id)).join(
            Module, Module.id == Lesson.module_id
        ).filter(Module.course_id == course_id).scalar() or 0
        
        if total_lessons == 0:
            return False
        
        # Get completed lessons
        completed_lessons = db.query(func.count(LessonProgress.id)).filter(
            and_(
                LessonProgress.student_id == student_id,
                LessonProgress.completed == True,
                LessonProgress.lesson_id.in_(
                    db.query(Lesson.id).join(
                        Module, Module.id == Lesson.module_id
                    ).filter(Module.course_id == course_id)
                )
            )
        ).scalar() or 0
        
        return completed_lessons >= total_lessons
    except Exception as e:
        logger.error(f"Error checking course completion: {str(e)}")
        return False
