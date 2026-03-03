from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime
from database import get_db
from models import LessonProgress, Lesson, Module, Enrollment, Course
from models.user import User
from schemas.progress import (
    LessonProgressResponse,
    LessonProgressWithDetailsResponse,
    StudentLessonProgressResponse,
    ProgressStatisticsResponse,
)
from schemas.enrollment import EnrollmentResponse
from routes.auth import get_current_user
from services.badge_service import check_and_award_badges

router = APIRouter(
    prefix="/lessons",
    tags=["lessons"],
)


# ==================== LESSON PROGRESS ENDPOINTS ====================

@router.post("/{lesson_id}/complete", response_model=LessonProgressResponse)
def complete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark a lesson as complete for the authenticated student.
    
    This endpoint:
    1. Updates LessonProgress to mark lesson as completed
    2. Recalculates the course enrollment progress
    3. Updates enrollment completion status if all lessons are done
    
    Returns the updated lesson progress and updated enrollment progress.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    # Get or create lesson progress
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not lesson_progress:
        # Create new lesson progress entry
        lesson_progress = LessonProgress(
            student_id=current_user.id,
            lesson_id=lesson_id,
            completed=True,
            completion_date=datetime.utcnow()
        )
        db.add(lesson_progress)
    else:
        # Update existing entry
        if not lesson_progress.completed:
            lesson_progress.completed = True
            lesson_progress.completion_date = datetime.utcnow()
        else:
            # Lesson already completed
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This lesson is already marked as completed"
            )
    
    db.commit()
    
    # Get the module and course to find the enrollment
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    if not module:
        db.refresh(lesson_progress)
        return lesson_progress
    
    course_id = module.course_id
    
    # Find the enrollment
    enrollment = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == current_user.id,
            Enrollment.course_id == course_id
        )
    ).first()
    
    if enrollment:
        # Recalculate course progress
        _update_course_progress(enrollment, db, course_id, current_user.id)
    
    # Check and award badges for student achievements
    newly_earned_badges = check_and_award_badges(current_user.id, db)
    
    db.refresh(lesson_progress)
    return lesson_progress


@router.get("/{lesson_id}/progress", response_model=LessonProgressResponse)
def get_lesson_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the authenticated student's progress on a specific lesson.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not lesson_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't started this lesson yet"
        )
    
    return lesson_progress


@router.post("/{lesson_id}/start", response_model=LessonProgressResponse, status_code=status.HTTP_201_CREATED)
def start_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Mark the start of a lesson for the authenticated student.
    
    Creates a LessonProgress entry if one doesn't exist.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    # Check if already started
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if lesson_progress:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already started this lesson"
        )
    
    # Create new lesson progress entry
    lesson_progress = LessonProgress(
        student_id=current_user.id,
        lesson_id=lesson_id,
        completed=False
    )
    db.add(lesson_progress)
    db.commit()
    db.refresh(lesson_progress)
    
    return lesson_progress


@router.get("/module/{module_id}/progress", response_model=list[StudentLessonProgressResponse])
def get_module_progress(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get the authenticated student's progress on all lessons in a module.
    """
    # Verify module exists
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    # Get all lessons in the module
    lessons = db.query(Lesson).filter(Lesson.module_id == module_id).all()
    lesson_ids = [lesson.id for lesson in lessons]
    
    # Get progress for all lessons
    progress_list = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id.in_(lesson_ids)
        )
    ).all()
    
    return progress_list


@router.get("/course/{course_id}/progress", response_model=ProgressStatisticsResponse)
def get_course_progress_statistics(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive progress statistics for a student in a specific course.
    
    Returns:
    - Total lessons started
    - Total lessons completed
    - Overall completion percentage
    - Progress breakdown by module
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    # Get all modules in the course
    modules = db.query(Module).filter(Module.course_id == course_id).all()
    
    modules_progress = []
    total_lessons_started = 0
    total_lessons_completed = 0
    
    for module in modules:
        # Get all lessons in the module
        lessons = db.query(Lesson).filter(Lesson.module_id == module.id).all()
        total_lessons = len(lessons)
        
        if total_lessons == 0:
            continue
        
        lesson_ids = [lesson.id for lesson in lessons]
        
        # Get progress for all lessons
        progress_list = db.query(LessonProgress).filter(
            and_(
                LessonProgress.student_id == current_user.id,
                LessonProgress.lesson_id.in_(lesson_ids)
            )
        ).all()
        
        completed_lessons = sum(1 for p in progress_list if p.completed)
        completion_percentage = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        modules_progress.append({
            "module_id": module.id,
            "module_title": module.title,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "completion_percentage": completion_percentage,
        })
        
        total_lessons_started += len(progress_list)
        total_lessons_completed += completed_lessons
    
    # Calculate overall completion percentage
    overall_completion_percentage = 0.0
    if total_lessons_started > 0:
        overall_completion_percentage = (total_lessons_completed / total_lessons_started) * 100
    
    return {
        "total_lessons_started": total_lessons_started,
        "total_lessons_completed": total_lessons_completed,
        "overall_completion_percentage": overall_completion_percentage,
        "modules_progress": modules_progress,
    }


@router.delete("/{lesson_id}/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset_lesson_progress(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reset a lesson's progress for the authenticated student.
    
    This marks the lesson as incomplete and removes the completion date.
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    lesson_progress = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == current_user.id,
            LessonProgress.lesson_id == lesson_id
        )
    ).first()
    
    if not lesson_progress:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You haven't started this lesson yet"
        )
    
    # Reset progress
    lesson_progress.completed = False
    lesson_progress.completion_date = None
    
    db.commit()
    
    # Recalculate course progress
    module = db.query(Module).filter(Module.id == lesson.module_id).first()
    if module:
        course_id = module.course_id
        enrollment = db.query(Enrollment).filter(
            and_(
                Enrollment.student_id == current_user.id,
                Enrollment.course_id == course_id
            )
        ).first()
        
        if enrollment:
            _update_course_progress(enrollment, db, course_id, current_user.id)


# ==================== HELPER FUNCTIONS ====================

def _update_course_progress(
    enrollment: Enrollment,
    db: Session,
    course_id: int,
    student_id: int
):
    """
    Helper function to recalculate and update course enrollment progress.
    
    Calculates the percentage of lessons completed and updates the enrollment record.
    Also marks the enrollment as completed if all lessons are done.
    """
    # Get all lessons in the course
    total_lessons = db.query(func.count(Lesson.id)).join(
        Module, Lesson.module_id == Module.id
    ).filter(
        Module.course_id == course_id
    ).scalar()
    
    if total_lessons == 0:
        return
    
    # Get all lesson IDs in the course
    lesson_ids = db.query(Lesson.id).join(
        Module, Lesson.module_id == Module.id
    ).filter(
        Module.course_id == course_id
    ).all()
    
    lesson_id_list = [lesson_id[0] for lesson_id in lesson_ids]
    
    # Count completed lessons
    completed_lessons = db.query(func.count(LessonProgress.id)).filter(
        and_(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id.in_(lesson_id_list),
            LessonProgress.completed == True
        )
    ).scalar()
    
    # Calculate progress percentage
    progress_percentage = (completed_lessons / total_lessons) * 100
    
    # Update enrollment
    enrollment.progress_percentage = progress_percentage
    
    # Mark as completed if all lessons are done
    if completed_lessons == total_lessons:
        enrollment.completed = True
    else:
        enrollment.completed = False
    
    db.commit()
    db.refresh(enrollment)
