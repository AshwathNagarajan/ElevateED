from services.auth import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    require_role
)
from services.recommendation_engine import (
    analyze_student_performance,
    get_student_quiz_statistics,
    unlock_next_level
)
from services.badge_service import (
    check_and_award_badges,
    get_student_badges
)

__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "verify_token",
    "require_role",
    "analyze_student_performance",
    "get_student_quiz_statistics",
    "unlock_next_level",
    "check_and_award_badges",
    "get_student_badges"
]
