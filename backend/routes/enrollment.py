from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Enrollment, Course, Lesson, Module
from models.user import User
from schemas.enrollment import (
    EnrollmentCreate,
    EnrollmentCreateRequest,
    EnrollmentResponse,
    EnrollmentDetailResponse,
    StudentEnrollmentsResponse,
)
from routes.auth import get_current_user
from sqlalchemy import func, and_

router = APIRouter(
    prefix="/enrollments",
    tags=["enrollments"],
)


# ==================== ENROLLMENT ENDPOINTS ====================

@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def create_enrollment(
    enrollment_request: EnrollmentCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enroll the authenticated user in a course.
    
    Accepts JSON body with course_id.
    """
    course_id = enrollment_request.course_id
    
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    # Check if already enrolled
    existing = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course"
        )
    
    # Create enrollment
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        progress_percentage=0.0,
        completed=False,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.post("/enroll/{course_id}", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_in_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Enroll the authenticated student in a course.
    
    - Returns HTTP 400 if student is already enrolled
    - Returns HTTP 404 if course doesn't exist
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    # Check if student is already enrolled
    existing_enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already enrolled in this course"
        )
    
    # Create new enrollment
    enrollment = Enrollment(
        student_id=current_user.id,
        course_id=course_id,
        progress_percentage=0.0,
        completed=False,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.get("/my-courses", response_model=list[StudentEnrollmentsResponse])
def get_my_courses(
    skip: int = 0,
    limit: int = 100,
    completed_only: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all courses the authenticated student is enrolled in.
    
    - **skip**: Number of enrollments to skip for pagination
    - **limit**: Maximum number of enrollments to return
    - **completed_only**: Filter to show only completed courses
    """
    query = db.query(Enrollment).filter(Enrollment.student_id == current_user.id)
    
    if completed_only:
        query = query.filter(Enrollment.completed == True)
    
    enrollments = query.offset(skip).limit(limit).all()
    return enrollments


@router.get("/course-progress/{course_id}", response_model=EnrollmentResponse)
def get_course_progress(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the authenticated student's progress in a specific course.
    
    Returns progress percentage and completion status.
    """
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You are not enrolled in this course"
        )
    
    return enrollment


@router.put("/update-progress/{enrollment_id}", response_model=EnrollmentResponse)
def update_course_progress(
    enrollment_id: int,
    lessons_completed: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update student's course progress when a lesson is completed.
    
    - **lessons_completed**: Number of lessons completed by the student
    - Automatically calculates progress percentage based on total lessons in course
    - Marks course as completed when all lessons are done
    """
    # Verify enrollment exists and belongs to current user
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.id == enrollment_id,
            Enrollment.student_id == current_user.id
        )
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Get total number of lessons in the course
    total_lessons = db.query(func.count(Lesson.id)).join(
        Module, Lesson.module_id == Module.id
    ).filter(
        Module.course_id == enrollment.course_id
    ).scalar()
    
    if total_lessons == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course has no lessons"
        )
    
    # Calculate progress percentage
    progress_percentage = (lessons_completed / total_lessons) * 100
    
    # Ensure progress doesn't exceed 100%
    if progress_percentage > 100:
        progress_percentage = 100
    
    # Update enrollment
    enrollment.progress_percentage = progress_percentage
    
    # Mark as completed if progress reaches 100%
    if progress_percentage >= 100:
        enrollment.completed = True
    
    db.commit()
    db.refresh(enrollment)
    
    return enrollment


@router.get("/student/{student_id}/enrollments", response_model=list[EnrollmentResponse])
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all enrollments for a specific student.
    
    Only the student themselves or an admin can view this information.
    """
    # Check if user has permission
    if current_user.id != student_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this student's enrollments"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student_id
    ).all()
    
    return enrollments


@router.get("/course/{course_id}/students", response_model=list[EnrollmentResponse])
def get_course_enrollments(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all students enrolled in a specific course.
    
    Only admins can access this endpoint.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    return enrollments


@router.delete("/unenroll/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def unenroll_from_course(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Unenroll the authenticated student from a course.
    
    Students can only unenroll from their own courses.
    Admins can unenroll any student.
    """
    enrollment = db.query(Enrollment).filter(
        Enrollment.id == enrollment_id
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    # Check permission
    if current_user.id != enrollment.student_id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to unenroll from this course"
        )
    
    db.delete(enrollment)
    db.commit()


@router.get("/stats/completion-rate", response_model=dict)
def get_completion_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get completion statistics for the authenticated student.
    
    Returns:
    - Total enrolled courses
    - Completed courses
    - In-progress courses
    - Overall completion percentage
    - Average progress across all courses
    """
    # Get all enrollments for current student
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == current_user.id
    ).all()
    
    if not enrollments:
        return {
            "total_courses": 0,
            "completed_courses": 0,
            "in_progress_courses": 0,
            "overall_completion_percentage": 0.0,
            "average_progress": 0.0,
        }
    
    total_courses = len(enrollments)
    completed_courses = sum(1 for e in enrollments if e.completed)
    in_progress_courses = total_courses - completed_courses
    overall_completion_percentage = (completed_courses / total_courses) * 100
    average_progress = sum(e.progress_percentage for e in enrollments) / total_courses
    
    return {
        "total_courses": total_courses,
        "completed_courses": completed_courses,
        "in_progress_courses": in_progress_courses,
        "overall_completion_percentage": overall_completion_percentage,
        "average_progress": average_progress,
    }
