from collections import defaultdict
from typing import Dict

from sqlalchemy.orm import Session

from models import Attendance, Course, Enrollment, LessonProgress, Quiz, QuizSubmission, Student
from models.course import Module
from models.user import User


TRACK_FEATURES = {
    "Mathematics": "math_score",
    "Science": "logic_score",
    "English": "verbal_score",
    "Social Studies": "verbal_score",
    "Computer Basics": "logic_score",
    "Engineering": "logic_score",
    "Computer Science": "logic_score",
    "Data Science": "math_score",
    "Business Analytics": "math_score",
    "Design": "creative_score",
    "Humanities": "verbal_score",
    "Life Science": "logic_score",
    "Commerce": "math_score",
}


def build_learning_feature_vector(user: User, student: Student, db: Session) -> Dict:
    """
    Convert a student's real activity into ML-ready learning signals.
    """
    submissions = db.query(QuizSubmission).filter(QuizSubmission.student_id == student.id).all()
    lesson_progress = db.query(LessonProgress).filter(LessonProgress.student_id == user.id).all()
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == user.id).all()
    attendance = db.query(Attendance).filter(Attendance.student_id == student.id).all()

    feature_scores = {
        "math_score": 50,
        "verbal_score": 50,
        "logic_score": 50,
        "creative_score": 50,
    }
    track_stats = defaultdict(lambda: {"attempts": 0, "score": 0})

    for submission in submissions:
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
        if not quiz or not quiz.lesson:
            continue
        module = db.query(Module).filter(Module.id == quiz.lesson.module_id).first()
        course = db.query(Course).filter(Course.id == module.course_id).first() if module else None
        if not course:
            continue
        track_stats[course.track_type]["attempts"] += 1
        track_stats[course.track_type]["score"] += submission.score or 0

    for track, stats in track_stats.items():
        feature = TRACK_FEATURES.get(track)
        if feature and stats["attempts"]:
            feature_scores[feature] = max(feature_scores[feature], round(stats["score"] / stats["attempts"]))

    quiz_attempts = len(submissions)
    correct_attempts = sum(1 for item in submissions if item.is_correct)
    quiz_success_rate = (correct_attempts / quiz_attempts) if quiz_attempts else 0.0
    completed_lessons = sum(1 for item in lesson_progress if item.completed)
    avg_course_progress = (
        sum(item.progress_percentage or 0 for item in enrollments) / len(enrollments)
        if enrollments else 0.0
    )

    if attendance:
        attendance_rate = sum(1 for item in attendance if item.present) / len(attendance)
    else:
        attendance_rate = 0.75

    confidence_level = max(
        0.25,
        min(
            1.0,
            (quiz_success_rate * 0.55)
            + (min(completed_lessons, 12) / 12 * 0.25)
            + (min(avg_course_progress, 100) / 100 * 0.20),
        ),
    )
    lesson_completion_rate = max(
        0.0,
        min(1.0, (avg_course_progress / 100 * 0.65) + (completed_lessons / 20 * 0.35)),
    )
    learning_pace = max(
        0.0,
        min(1.0, (lesson_completion_rate * 0.55) + (quiz_success_rate * 0.25) + (confidence_level * 0.20)),
    )
    consistency_score = max(
        0.0,
        min(1.0, (attendance_rate * 0.60) + (lesson_completion_rate * 0.40)),
    )

    evidence_count = quiz_attempts + completed_lessons + len(attendance)

    return {
        **feature_scores,
        "confidence_level": round(confidence_level, 2),
        "attendance_rate": round(attendance_rate, 2),
        "quiz_success_rate": round(quiz_success_rate, 2),
        "lesson_completion_rate": round(lesson_completion_rate, 2),
        "learning_pace": round(learning_pace, 2),
        "consistency_score": round(consistency_score, 2),
        "evidence_count": evidence_count,
        "quiz_attempts": quiz_attempts,
        "lessons_completed": completed_lessons,
        "attendance_records": len(attendance),
        "average_course_progress": round(avg_course_progress, 1),
        "readiness": "ready" if evidence_count >= 8 and quiz_attempts >= 3 else "collecting_signals",
    }
