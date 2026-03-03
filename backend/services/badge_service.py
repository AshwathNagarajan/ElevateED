from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Student, Badge, StudentBadge, Enrollment, LessonProgress, QuizSubmission, Quiz, Lesson, Module
from datetime import datetime, timedelta
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


def check_and_award_badges(student_id: int, db: Session) -> List[Dict]:
    """
    Check and award badges to a student based on their achievements.
    
    This function is triggered after lesson completion or quiz submission.
    It checks all badge conditions and automatically awards new badges.
    
    Conditions checked:
    - COMPLETE_COURSE: Student completes 1+ course
    - LEARNING_STREAK: Student learns 7+ consecutive days
    - HIGH_SCORE: Student achieves ≥80% average quiz score
    - QUIZ_MASTER: Student completes 10+ quizzes
    - ATTENDANCE_PERFECT: Student has 100% attendance
    - FIRST_LESSON: Student completes first lesson
    - MODULE_COMPLETION: Student completes a module
    - PRACTICE_DEDICATION: Student attempts 50+ quizzes
    
    Args:
        student_id: ID of the student to check
        db: Database session
        
    Returns:
        List of newly earned badges with details:
        - badge_id: ID of earned badge
        - badge_name: Name of the badge
        - description: Badge description
        - points: Points awarded
        - message: Achievement message
    """
    
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        logger.warning(f"Student {student_id} not found for badge check")
        return []
    
    newly_earned = []
    
    # Get all active badges
    badges = db.query(Badge).filter(Badge.is_active == True).all()
    
    # Get already earned badges for this student
    earned_badge_ids = db.query(StudentBadge.badge_id).filter(
        StudentBadge.student_id == student_id
    ).all()
    earned_badge_ids = {badge_id[0] for badge_id in earned_badge_ids}
    
    for badge in badges:
        # Skip if student already earned this badge
        if badge.id in earned_badge_ids:
            continue
        
        # Check condition and award if met
        if badge.condition_type.value == "complete_course":
            if _check_complete_course(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "learning_streak":
            if _check_learning_streak(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "high_score":
            if _check_high_score(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "quiz_master":
            if _check_quiz_master(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "attendance_perfect":
            if _check_perfect_attendance(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "first_lesson":
            if _check_first_lesson(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "module_completion":
            if _check_module_completion(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
        
        elif badge.condition_type.value == "practice_dedication":
            if _check_practice_dedication(student_id, db):
                newly_earned.append(_award_badge(student_id, badge, db))
    
    return newly_earned


# ==================== Badge Condition Checkers ====================

def _check_complete_course(student_id: int, db: Session) -> bool:
    """Check if student has completed 1+ course."""
    completed_courses = db.query(Enrollment).filter(
        and_(
            Enrollment.student_id == student_id,
            Enrollment.completed == True
        )
    ).count()
    return completed_courses >= 1


def _check_learning_streak(student_id: int, db: Session) -> bool:
    """Check if student has 7+ consecutive days of learning."""
    # Get all lesson progress records ordered by date
    progress_records = db.query(LessonProgress).filter(
        LessonProgress.student_id == student_id
    ).order_by(LessonProgress.started_at).all()
    
    if not progress_records:
        return False
    
    # Calculate consecutive days
    dates = set()
    for record in progress_records:
        if record.started_at:
            dates.add(record.started_at.date())
    
    if len(dates) < 7:
        return False
    
    # Check if there are 7 consecutive days in the dates
    sorted_dates = sorted(list(dates))
    consecutive_count = 1
    
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            consecutive_count += 1
            if consecutive_count >= 7:
                return True
        else:
            consecutive_count = 1
    
    return consecutive_count >= 7


def _check_high_score(student_id: int, db: Session) -> bool:
    """Check if student has ≥80% average quiz score."""
    submissions = db.query(QuizSubmission).filter(
        QuizSubmission.student_id == student_id
    ).all()
    
    if len(submissions) < 5:  # Need at least 5 attempts
        return False
    
    average_score = sum(s.score for s in submissions) / len(submissions)
    return average_score >= 80


def _check_quiz_master(student_id: int, db: Session) -> bool:
    """Check if student has completed 10+ quizzes."""
    quiz_count = db.query(QuizSubmission).filter(
        QuizSubmission.student_id == student_id
    ).count()
    return quiz_count >= 10


def _check_perfect_attendance(student_id: int, db: Session) -> bool:
    """Check if student has 100% attendance."""
    from models import Attendance
    
    # Get all attendance records for this student
    attendance_records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).all()
    
    if len(attendance_records) < 5:  # Need at least 5 records
        return False
    
    # Check if all are marked present
    all_present = sum(1 for record in attendance_records if record.present)
    return all_present == len(attendance_records)


def _check_first_lesson(student_id: int, db: Session) -> bool:
    """Check if student has completed first lesson."""
    # Get first lesson ever created
    first_lesson = db.query(Lesson).order_by(Lesson.id).first()
    
    if not first_lesson:
        return False
    
    # Check if student completed this lesson
    completed = db.query(LessonProgress).filter(
        and_(
            LessonProgress.student_id == student_id,
            LessonProgress.lesson_id == first_lesson.id,
            LessonProgress.completed == True
        )
    ).first()
    
    return completed is not None


def _check_module_completion(student_id: int, db: Session) -> bool:
    """Check if student has completed 1+ module."""
    # A module is complete if all its lessons are completed
    modules = db.query(Module).all()
    
    for module in modules:
        total_lessons = len(module.lessons)
        if total_lessons == 0:
            continue
        
        completed_lessons = db.query(LessonProgress).filter(
            and_(
                LessonProgress.student_id == student_id,
                Lesson.module_id == module.id,
                LessonProgress.completed == True
            )
        ).join(Lesson).count()
        
        if completed_lessons == total_lessons:
            return True
    
    return False


def _check_practice_dedication(student_id: int, db: Session) -> bool:
    """Check if student has attempted 50+ quizzes."""
    quiz_count = db.query(QuizSubmission).filter(
        QuizSubmission.student_id == student_id
    ).count()
    return quiz_count >= 50


# ==================== Badge Award Helper ====================

def _award_badge(student_id: int, badge: Badge, db: Session) -> Dict:
    """
    Award a badge to a student.
    
    Args:
        student_id: ID of student receiving badge
        badge: Badge object to award
        db: Database session
        
    Returns:
        Dictionary with achievement details
    """
    try:
        # Create StudentBadge record
        student_badge = StudentBadge(
            student_id=student_id,
            badge_id=badge.id,
            earned_at=datetime.utcnow(),
            context_data=None
        )
        
        db.add(student_badge)
        db.commit()
        
        logger.info(f"Student {student_id} earned badge '{badge.name}' ({badge.id})")
        
        return {
            "badge_id": badge.id,
            "badge_name": badge.name,
            "description": badge.description,
            "points": badge.points,
            "message": f"Congratulations! You earned the '{badge.name}' badge! (+{badge.points} points)"
        }
    
    except Exception as e:
        logger.error(f"Error awarding badge {badge.id} to student {student_id}: {str(e)}")
        return None


def get_student_badges(student_id: int, db: Session) -> Dict:
    """
    Get all badges earned by a student.
    
    Args:
        student_id: ID of the student
        db: Database session
        
    Returns:
        Dictionary with earned badges and total points
    """
    # Get all badges earned by this student
    student_badges = db.query(StudentBadge).filter(
        StudentBadge.student_id == student_id
    ).all()
    
    if not student_badges:
        return {
            "student_id": student_id,
            "total_badges": 0,
            "total_points": 0,
            "badges": []
        }
    
    # Calculate total points
    total_points = sum(sb.badge.points for sb in student_badges)
    
    # Format response
    badges_list = [
        {
            "badge_id": sb.badge_id,
            "badge_name": sb.badge.name,
            "description": sb.badge.description,
            "points": sb.badge.points,
            "color": sb.badge.color,
            "icon_url": sb.badge.icon_url,
            "earned_at": sb.earned_at,
            "context_data": sb.context_data
        }
        for sb in student_badges
    ]
    
    return {
        "student_id": student_id,
        "total_badges": len(student_badges),
        "total_points": total_points,
        "badges": badges_list
    }
