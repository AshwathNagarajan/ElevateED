from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from database import get_db
from models.weekly_skill_score import WeeklySkillScore
from schemas.weekly_skill_score import (
    WeeklySkillScoreCreate,
    WeeklySkillScoreResponse,
    SkillScoreUpdate
)
from services.skill_engine import calculate_skill_score

router = APIRouter(
    prefix="/skills",
    tags=["skills"],
)


@router.post("/update-weekly-score", response_model=WeeklySkillScoreResponse, status_code=status.HTTP_201_CREATED)
def update_weekly_score(
    score_data: WeeklySkillScoreCreate,
    db: Session = Depends(get_db)
):
    """
    Update weekly skill score for a student.
    
    Fetches quiz, project, attendance, and mentor rating scores,
    computes the overall skill score, and stores it in the WeeklySkillScore table.
    
    Args:
        score_data: Contains student_id, quiz_score, project_score, attendance_score, mentor_rating, week_ending
        db: Database session
    
    Returns:
        WeeklySkillScoreResponse: Created weekly skill score record
    """
    # Calculate the overall skill score using the skill engine
    skill_score = calculate_skill_score(
        quiz_score=score_data.quiz_score,
        project_score=score_data.project_score,
        attendance_score=score_data.attendance_score,
        mentor_rating=score_data.mentor_rating
    )
    
    # Create new weekly skill score record
    db_weekly_score = WeeklySkillScore(
        student_id=score_data.student_id,
        quiz_score=score_data.quiz_score,
        project_score=score_data.project_score,
        attendance_score=score_data.attendance_score,
        mentor_rating=score_data.mentor_rating,
        skill_score=skill_score,
        week_ending=score_data.week_ending
    )
    
    db.add(db_weekly_score)
    db.commit()
    db.refresh(db_weekly_score)
    
    return db_weekly_score


@router.get("/weekly-scores/{student_id}", response_model=list[WeeklySkillScoreResponse])
def get_student_weekly_scores(
    student_id: int,
    skip: int = 0,
    limit: int = 52,  # Default to 52 weeks (1 year)
    db: Session = Depends(get_db)
):
    """
    Retrieve weekly skill scores for a specific student.
    
    Args:
        student_id: The student ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        list[WeeklySkillScoreResponse]: List of weekly skill scores
    """
    scores = db.query(WeeklySkillScore).filter(
        WeeklySkillScore.student_id == student_id
    ).order_by(WeeklySkillScore.week_ending.desc()).offset(skip).limit(limit).all()
    
    return scores


@router.get("/weekly-score/{score_id}", response_model=WeeklySkillScoreResponse)
def get_weekly_score_by_id(
    score_id: int,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific weekly skill score record by ID.
    
    Args:
        score_id: The weekly skill score ID
        db: Database session
    
    Returns:
        WeeklySkillScoreResponse: The weekly skill score
    
    Raises:
        HTTPException: If the record is not found
    """
    score = db.query(WeeklySkillScore).filter(WeeklySkillScore.id == score_id).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly skill score with id {score_id} not found"
        )
    
    return score


@router.put("/weekly-score/{score_id}", response_model=WeeklySkillScoreResponse)
def update_weekly_score_components(
    score_id: int,
    update_data: SkillScoreUpdate,
    db: Session = Depends(get_db)
):
    """
    Update individual components of a weekly skill score and recalculate the overall score.
    
    Args:
        score_id: The weekly skill score ID
        update_data: Updated score components (any combination of quiz, project, attendance, mentor_rating)
        db: Database session
    
    Returns:
        WeeklySkillScoreResponse: Updated weekly skill score
    
    Raises:
        HTTPException: If the record is not found
    """
    score = db.query(WeeklySkillScore).filter(WeeklySkillScore.id == score_id).first()
    
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Weekly skill score with id {score_id} not found"
        )
    
    # Update individual scores if provided
    if update_data.quiz_score is not None:
        score.quiz_score = update_data.quiz_score
    if update_data.project_score is not None:
        score.project_score = update_data.project_score
    if update_data.attendance_score is not None:
        score.attendance_score = update_data.attendance_score
    if update_data.mentor_rating is not None:
        score.mentor_rating = update_data.mentor_rating
    
    # Recalculate the overall skill score
    score.skill_score = calculate_skill_score(
        quiz_score=score.quiz_score,
        project_score=score.project_score,
        attendance_score=score.attendance_score,
        mentor_rating=score.mentor_rating
    )
    
    db.commit()
    db.refresh(score)
    
    return score
