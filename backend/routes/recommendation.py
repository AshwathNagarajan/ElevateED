from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Student, Module, Lesson
from models.user import User
from routes.auth import get_current_user, get_student_for_user
from services.recommendation_engine import (
    analyze_student_performance,
    get_student_quiz_statistics,
    unlock_next_level
)
from schemas.recommendation import (
    RecommendationResponse,
    StudentPerformanceResponse,
    NextLevelResponse
)
from typing import List

router = APIRouter(
    prefix="/recommendations",
    tags=["recommendations"],
)


@router.get("/my-recommendations", response_model=List[RecommendationResponse])
def get_my_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized recommendations for the current student.
    
    Analyzes student's quiz performance and generates recommendations:
    - **revision**: Student failed >2 quizzes in a module (recommend review)
    - **next_level**: Student has ≥80% success rate (ready for advanced content)
    - **foundational_review**: Student has <50% success rate (needs basics reinforcement)
    
    Returns:
        List of personalized recommendations with:
        - type: Type of recommendation (revision, next_level, foundational_review)
        - module_id: ID of the module
        - module_name: Name of the module
        - message: Human-readable recommendation
        - score: Student's success percentage in that module
    """
    # Get student from current user
    student = get_student_for_user(db, current_user)
    
    # Analyze student performance and get recommendations
    recommendations = analyze_student_performance(student.id, db)
    
    if not recommendations:
        return []
    
    return recommendations


@router.get("/performance", response_model=StudentPerformanceResponse)
def get_student_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get comprehensive quiz statistics and performance overview.
    
    Returns:
        - total_quizzes: Total quizzes attempted
        - passed: Number of quizzes passed
        - failed: Number of quizzes failed
        - success_percentage: Overall success rate
        - average_score: Average score across all quizzes
        - module_stats: Per-module performance breakdown
    """
    # Get student from current user
    student = get_student_for_user(db, current_user)
    
    # Get detailed quiz statistics
    stats = get_student_quiz_statistics(student.id, db)
    
    return stats


@router.get("/module/{module_id}/next-level", response_model=NextLevelResponse)
def check_next_level(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check if student qualifies to unlock the next level.
    
    Requirements to unlock next level:
    - ≥80% success rate in current module
    - Minimum 5 quiz attempts in current module
    
    Args:
        module_id: ID of the current module
        
    Returns:
        - unlocked: Boolean indicating if next level is unlocked
        - message: Description of the result
        - reason: Explanation if not unlocked
        - next_module: Details of next module if unlocked
    """
    # Get student from current user
    student = get_student_for_user(db, current_user)
    
    # Verify module exists
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    # Check if student can unlock next level
    result = unlock_next_level(student.id, module_id, db)
    
    return result


@router.get("/module/{module_id}/revision-lesson", response_model=dict)
def get_revision_lesson(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a revision lesson recommendation for a module.
    
    Called when student has failed >2 quizzes in the module.
    Returns the first lesson in the module as a revision opportunity.
    
    Args:
        module_id: ID of the module needing revision
        
    Returns:
        - lesson_id: ID of the revision lesson
        - lesson_title: Title of the lesson
        - lesson_content: Lesson content/description
        - video_url: Video URL if available
        - recommendation: Why this lesson is recommended
    """
    # Verify module exists
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with ID {module_id} not found"
        )
    
    # Get first lesson in module for revision
    revision_lesson = db.query(Lesson).filter(
        Lesson.module_id == module_id
    ).order_by(Lesson.id).first()
    
    if not revision_lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No lessons found in module {module_id}"
        )
    
    return {
        "lesson_id": revision_lesson.id,
        "lesson_title": revision_lesson.title,
        "lesson_content": revision_lesson.content,
        "video_url": revision_lesson.video_url,
        "duration_minutes": revision_lesson.duration_minutes,
        "recommendation": f"Review {revision_lesson.title} to strengthen your understanding of {module.title}",
        "module_id": module_id,
        "module_name": module.title
    }


@router.get("/practice-recommendations", response_model=List[dict])
def get_practice_recommendations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get personalized practice recommendations based on performance.
    
    Recommends:
    - Modules where student needs more practice (<80% success)
    - Specific lesson areas to focus on
    - Suggested quiz topics to review
    
    Returns:
        List of practice recommendations with focus areas and difficulty
    """
    # Get student from current user
    student = get_student_for_user(db, current_user)
    
    # Get recommendations
    recommendations = analyze_student_performance(student.id, db)
    
    # Filter for practice-related recommendations (revision and foundational review)
    practice_recommendations = [
        {
            "module_id": rec.get("module_id"),
            "module_name": rec.get("module_name"),
            "message": rec.get("message"),
            "focus_area": "Conceptual Understanding" if rec.get("type") == "foundational_review" else "Applied Skills",
            "difficulty": "Beginner" if rec.get("type") == "foundational_review" else "Intermediate",
            "priority": "High" if rec.get("type") == "foundational_review" else "Medium",
            "success_rate": rec.get("score", 0),
            "recommendation_type": rec.get("type")
        }
        for rec in recommendations if rec.get("type") in ["revision", "foundational_review"]
    ]
    
    # Sort by priority and success rate
    practice_recommendations.sort(
        key=lambda x: (x["priority"] != "High", x["success_rate"]),
        reverse=False
    )
    
    return practice_recommendations
