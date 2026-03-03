"""
Skill engine for calculating student skill scores based on multiple metrics.
"""


def calculate_skill_score(
    quiz_score: float,
    project_score: float,
    attendance_score: float,
    mentor_rating: float
) -> float:
    """
    Calculate the overall skill score for a student.
    
    Skill Score = (Quiz * 0.4) + (Project * 0.3) + (Attendance * 0.2) + (Mentor Rating * 0.1)
    
    Args:
        quiz_score: Quiz performance score (0-100)
        project_score: Project completion score (0-100)
        attendance_score: Attendance rate score (0-100)
        mentor_rating: Mentor rating score (0-100)
    
    Returns:
        float: Final skill score rounded to 2 decimal places
    
    Example:
        >>> calculate_skill_score(85, 90, 95, 88)
        88.9
    """
    # Calculate weighted skill score
    skill_score = (
        (quiz_score * 0.4) +
        (project_score * 0.3) +
        (attendance_score * 0.2) +
        (mentor_rating * 0.1)
    )
    
    # Return rounded to 2 decimal places
    return round(skill_score, 2)
