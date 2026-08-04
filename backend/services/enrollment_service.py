"""
Enrollment service for handling student course enrollments.
Provides clean interfaces for enrollment operations.
"""

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from models import Enrollment, Course
from schemas.enrollment import (
    EnrollmentResponse,
    StudentEnrollmentsResponse,
)
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ENROLLMENT CREATION
# ============================================================================

def enroll_student_in_course(
    student_id: int,
    course_id: int,
    db: Session
) -> EnrollmentResponse:
    """
    Enroll a student in a course.
    
    Args:
        student_id: ID of the student (user_id)
        course_id: ID of the course
        db: Database session
        
    Returns:
        EnrollmentResponse with enrollment details
        
    Raises:
        ValueError: If course not found or already enrolled
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        logger.warning(f"Enrollment failed: course {course_id} not found for student {student_id}")
        raise ValueError(f"Course with id {course_id} not found")
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if existing:
        logger.warning(f"Enrollment failed: student {student_id} already enrolled in course {course_id}")
        raise ValueError("You are already enrolled in this course")
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id,
        progress_percentage=0.0,
        completed=False,
    )
    
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    logger.info(f"Student {student_id} enrolled in course {course_id}")
    return enrollment


# ============================================================================
# ENROLLMENT RETRIEVAL
# ============================================================================

def get_student_enrollments(
    student_id: int,
    db: Session,
    skip: int = 0,
    limit: int = 100,
    completed_only: bool = False
) -> List[StudentEnrollmentsResponse]:
    """
    Get all courses a student is enrolled in with full course details.
    
    Args:
        student_id: ID of the student (user_id)
        db: Database session
        skip: Pagination offset
        limit: Pagination limit
        completed_only: Filter to completed courses only
        
    Returns:
        List of StudentEnrollmentsResponse
    """
    try:
        query = db.query(Enrollment).options(
            joinedload(Enrollment.course)
        ).filter(Enrollment.student_id == student_id)
        
        if completed_only:
            query = query.filter(Enrollment.completed == True)
        
        enrollments = query.offset(skip).limit(limit).all()
        
        # Transform enrollments to include full course details
        result = []
        for enrollment in enrollments:
            course = enrollment.course
            if course:
                result.append(StudentEnrollmentsResponse(
                    enrollment_id=enrollment.id,
                    course_id=course.id,
                    course_title=course.title,
                    course_description=course.description,
                    track_type=course.track_type,
                    level=course.level,
                    instructor=course.instructor,
                    duration_hours=course.duration_hours,
                    thumbnail_url=course.thumbnail_url,
                    progress_percentage=enrollment.progress_percentage or 0.0,
                    completed=enrollment.completed or False,
                    enrolled_at=enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
                ))
        
        return result
    except Exception as e:
        logger.error(f"Error retrieving enrollments for student {student_id}: {str(e)}")
        return []


# ============================================================================
# ENROLLMENT VALIDATION
# ============================================================================

def is_student_enrolled(
    student_id: int,
    course_id: int,
    db: Session
) -> bool:
    """
    Check if a student is enrolled in a course.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        db: Database session
        
    Returns:
        True if enrolled, False otherwise
    """
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    return enrollment is not None


def get_enrollment(
    student_id: int,
    course_id: int,
    db: Session
) -> Optional[Enrollment]:
    """
    Get a specific enrollment record.
    
    Args:
        student_id: ID of the student
        course_id: ID of the course
        db: Database session
        
    Returns:
        Enrollment object or None if not found
    """
    return db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id
        )
    ).first()


# ============================================================================
# ENROLLMENT UPDATES
# ============================================================================

def update_enrollment_progress(
    enrollment_id: int,
    progress_percentage: float,
    db: Session
) -> Optional[Enrollment]:
    """
    Update an enrollment's progress percentage.
    
    Args:
        enrollment_id: ID of the enrollment
        progress_percentage: New progress value (0-100)
        db: Database session
        
    Returns:
        Updated Enrollment or None if not found
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        return None
    
    enrollment.progress_percentage = min(progress_percentage, 100.0)
    
    # Mark as completed if progress is 100%
    if progress_percentage >= 100.0:
        enrollment.completed = True
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


def mark_enrollment_completed(
    enrollment_id: int,
    db: Session
) -> Optional[Enrollment]:
    """
    Mark an enrollment as completed.
    
    Args:
        enrollment_id: ID of the enrollment
        db: Database session
        
    Returns:
        Updated Enrollment or None if not found
    """
    enrollment = db.query(Enrollment).filter(Enrollment.id == enrollment_id).first()
    if not enrollment:
        return None
    
    enrollment.completed = True
    enrollment.progress_percentage = 100.0
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment
