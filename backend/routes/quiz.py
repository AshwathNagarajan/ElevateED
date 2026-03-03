from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Quiz, QuizSubmission, Student, Lesson
from schemas.quiz import (
    QuizWithoutAnswer,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
)
from routes.auth import get_current_user
from services.badge_service import check_and_award_badges
from typing import List

router = APIRouter(
    prefix="/quizzes",
    tags=["quizzes"]
)


@router.get("/lessons/{lesson_id}", response_model=List[QuizWithoutAnswer])
def get_lesson_quizzes(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all quizzes for a specific lesson.
    
    Args:
        lesson_id: ID of the lesson
        
    Returns:
        List of quizzes for the lesson (without correct answers)
    """
    # Verify lesson exists
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with ID {lesson_id} not found"
        )
    
    # Get all quizzes for the lesson
    quizzes = db.query(Quiz).filter(Quiz.lesson_id == lesson_id).all()
    
    return quizzes


@router.post("/{quiz_id}/submit", response_model=QuizSubmissionResponse)
def submit_quiz(
    quiz_id: int,
    submission_data: QuizSubmissionRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Submit an answer to a quiz question.
    
    Automatically calculates the score based on correctness:
    - Correct answer: score = 100, is_correct = True
    - Incorrect answer: score = 0, is_correct = False
    
    Args:
        quiz_id: ID of the quiz being answered
        submission_data: Student's selected answer
        
    Returns:
        Quiz submission record with calculated score
    """
    # Verify quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found"
        )
    
    # Get student from current user
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found for current user"
        )
    
    # Calculate score: 100 if correct, 0 if incorrect
    is_correct = submission_data.selected_answer.value == quiz.correct_answer.value
    score = 100 if is_correct else 0
    
    # Create quiz submission record
    submission = QuizSubmission(
        student_id=student.id,
        quiz_id=quiz_id,
        selected_answer=submission_data.selected_answer,
        score=score,
        is_correct=is_correct
    )
    
    # Save to database
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    # Check and award badges for student achievements
    newly_earned_badges = check_and_award_badges(student.id, db)
    
    # Add quiz details to response
    submission_response = QuizSubmissionResponse(
        id=submission.id,
        student_id=submission.student_id,
        quiz_id=submission.quiz_id,
        selected_answer=submission.selected_answer,
        score=submission.score,
        is_correct=submission.is_correct,
        submitted_at=submission.submitted_at,
        question=quiz.question,
        correct_answer=quiz.correct_answer
    )
    
    return submission_response


@router.get("/{quiz_id}/submissions", response_model=List[QuizSubmissionResponse])
def get_quiz_submissions(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all submissions for a quiz (for admin/teacher analytics).
    
    Args:
        quiz_id: ID of the quiz
        
    Returns:
        List of all submissions for the quiz
    """
    # Verify quiz exists
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Quiz with ID {quiz_id} not found"
        )
    
    # Get all submissions for the quiz
    submissions = db.query(QuizSubmission).filter(QuizSubmission.quiz_id == quiz_id).all()
    
    # Transform to response with quiz details
    result = []
    for submission in submissions:
        result.append(
            QuizSubmissionResponse(
                id=submission.id,
                student_id=submission.student_id,
                quiz_id=submission.quiz_id,
                selected_answer=submission.selected_answer,
                score=submission.score,
                is_correct=submission.is_correct,
                submitted_at=submission.submitted_at,
                question=quiz.question,
                correct_answer=quiz.correct_answer
            )
        )
    
    return result


@router.get("/student/my-submissions", response_model=List[QuizSubmissionResponse])
def get_my_quiz_submissions(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all quiz submissions for the current student.
    
    Returns:
        List of student's quiz submissions
    """
    # Get student from current user
    student = db.query(Student).filter(Student.id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found for current user"
        )
    
    # Get all submissions for this student
    submissions = db.query(QuizSubmission).filter(
        QuizSubmission.student_id == student.id
    ).all()
    
    # Transform to response with quiz details
    result = []
    for submission in submissions:
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
        if quiz:
            result.append(
                QuizSubmissionResponse(
                    id=submission.id,
                    student_id=submission.student_id,
                    quiz_id=submission.quiz_id,
                    selected_answer=submission.selected_answer,
                    score=submission.score,
                    is_correct=submission.is_correct,
                    submitted_at=submission.submitted_at,
                    question=quiz.question,
                    correct_answer=quiz.correct_answer
                )
            )
    
    return result
