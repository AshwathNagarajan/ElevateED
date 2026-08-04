"""
Quiz service for handling quiz submissions and related business logic.
Provides clean interfaces for quiz operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import Quiz, QuizSubmission, Student, Lesson
from models.user import User
from services.badge_service import check_and_award_badges
from schemas.quiz import QuizSubmissionResponse
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# STUDENT MANAGEMENT
# ============================================================================

def get_or_create_student(user: User, db: Session) -> Student:
    """
    Get student record for a user, creating one if needed.
    
    Args:
        user: The User object
        db: Database session
        
    Returns:
        Student record
    """
    student = db.query(Student).filter(Student.user_id == user.id).first()
    
    if not student:
        logger.info(f"Auto-creating student record for user {user.id}")
        student = Student(
            user_id=user.id,
            name=user.full_name,
            age=0,
            guardian_contact="",
            interest_track=None
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    
    return student


# ============================================================================
# QUIZ SUBMISSION
# ============================================================================

def submit_quiz_answer(
    quiz_id: int,
    student_id: int,
    selected_answer: str,
    db: Session
) -> QuizSubmissionResponse:
    """
    Process a quiz submission and return the result.
    
    This function:
    1. Validates the quiz exists
    2. Checks for duplicate submissions
    3. Evaluates the answer
    4. Creates submission record
    5. Attempts badge awarding (wrapped to never fail submission)
    
    Args:
        quiz_id: ID of the quiz
        student_id: ID of the student submitting
        selected_answer: The answer selected by student
        db: Database session
        
    Returns:
        QuizSubmissionResponse with result and badge info
        
    Raises:
        ValueError: If quiz not found
        ValueError: If already submitted
    """
    # Get the quiz
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        logger.warning(f"Quiz submission failed: quiz {quiz_id} not found for student {student_id}")
        raise ValueError(f"Quiz with id {quiz_id} not found")
    
    # Check for duplicate submission
    existing_submission = db.query(QuizSubmission).filter(
        and_(
            QuizSubmission.quiz_id == quiz_id,
            QuizSubmission.student_id == student_id
        )
    ).first()
    
    if existing_submission:
        logger.warning(f"Duplicate quiz submission attempt: student {student_id}, quiz {quiz_id}")
        raise ValueError("You have already submitted this quiz")
    
    # Evaluate the answer
    is_correct = selected_answer == quiz.correct_answer
    score = 100.0 if is_correct else 0.0
    
    # Create submission record
    submission = QuizSubmission(
        quiz_id=quiz_id,
        student_id=student_id,
        selected_answer=selected_answer,
        is_correct=is_correct,
        score=score
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    logger.debug(f"Quiz submitted: student {student_id}, quiz {quiz_id}, correct={is_correct}")
    
    # Attempt to award badges (wrapped to never fail quiz submission)
    newly_earned_badges = []
    try:
        newly_earned_badges = check_and_award_badges(student_id, db)
    except Exception as e:
        logger.error(f"Badge awarding failed for student {student_id}: {str(e)}")
    
    # Build response
    lesson = quiz.lesson
    lesson_title = lesson.title if lesson else None
    lesson_id = lesson.id if lesson else None
    
    return QuizSubmissionResponse(
        submission_id=submission.id,
        quiz_id=quiz.id,
        lesson_id=lesson_id,
        lesson_title=lesson_title,
        is_correct=is_correct,
        score=score,
        correct_answer=quiz.correct_answer,
        message="Correct!" if is_correct else "Incorrect. Try again!",
        newly_earned_badges=newly_earned_badges
    )


# ============================================================================
# QUIZ RETRIEVAL
# ============================================================================

def get_lesson_quizzes_safe(lesson_id: int, db: Session) -> list:
    """
    Get all quizzes for a lesson without revealing correct answers.
    
    Args:
        lesson_id: ID of the lesson
        db: Database session
        
    Returns:
        List of quizzes (without correct_answer field)
    """
    quizzes = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).all()
    
    # Return quizzes without exposing correct answers
    return [
        {
            "id": q.id,
            "lesson_id": q.lesson_id,
            "question": q.question,
            "option_a": q.option_a,
            "option_b": q.option_b,
            "option_c": q.option_c,
            "option_d": q.option_d
        }
        for q in quizzes
    ]


def get_quiz_safe(quiz_id: int, db: Session) -> Optional[Dict]:
    """
    Get a specific quiz without revealing the correct answer.
    
    Args:
        quiz_id: ID of the quiz
        db: Database session
        
    Returns:
        Quiz data without correct_answer, or None if not found
    """
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        return None
    
    return {
        "id": quiz.id,
        "lesson_id": quiz.lesson_id,
        "question": quiz.question,
        "option_a": quiz.option_a,
        "option_b": quiz.option_b,
        "option_c": quiz.option_c,
        "option_d": quiz.option_d
    }
