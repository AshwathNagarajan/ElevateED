from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import StudentBadge
from models.user import User
from routes.auth import get_current_user, get_student_for_user


router = APIRouter(
    prefix="/badges",
    tags=["badges"],
)


@router.get("/my-achievements", response_model=dict)
def get_my_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the authenticated student's earned badges and achievement points.
    """
    student = get_student_for_user(db, current_user)
    earned_badges = (
        db.query(StudentBadge)
        .filter(StudentBadge.student_id == student.id)
        .order_by(StudentBadge.earned_at.desc())
        .all()
    )

    badges = []
    total_points = 0
    for earned in earned_badges:
        badge = earned.badge
        if not badge:
            continue
        total_points += badge.points or 0
        badges.append({
            "id": earned.id,
            "badge_id": badge.id,
            "name": badge.name,
            "description": badge.description,
            "condition_type": badge.condition_type.value,
            "color": badge.color,
            "points": badge.points,
            "earned_at": earned.earned_at,
            "context_data": earned.context_data,
        })

    return {
        "student_id": student.id,
        "total_badges": len(badges),
        "total_points": total_points,
        "badges": badges,
    }
