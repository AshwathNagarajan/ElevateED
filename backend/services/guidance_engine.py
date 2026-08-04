from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from models import Attendance, Course, Enrollment, LessonProgress, Quiz, QuizSubmission, Student
from models.course import Lesson, Module
from models.user import User
from services.learning_signal_service import build_learning_feature_vector
from services.ml_service import predict_track as predict_interest_track


TRACK_FEATURES = {
    "Mathematics": "math_score",
    "Science": "logic_score",
    "English": "verbal_score",
    "Social Studies": "verbal_score",
    "Computer Basics": "logic_score",
    "Engineering": "logic_score",
    "Computer Science": "logic_score",
    "Data Science": "math_score",
    "Design": "creative_score",
    "Humanities": "verbal_score",
    "Life Science": "logic_score",
    "Commerce": "math_score",
    "Product Management": "verbal_score",
    "Business Analytics": "math_score",
}

TRACK_ALIASES = {
    "Math": "Mathematics",
    "Social_Sciences": "Social Studies",
    "Social Sciences": "Social Studies",
    "Computers": "Computer Basics",
    "Computer_Basics": "Computer Basics",
    "CS": "Computer Science",
    "Computer_Science": "Computer Science",
    "Bio": "Life Science",
    "Life_Science": "Life Science",
}


def _canonical_track(track: Optional[str]) -> Optional[str]:
    if not track:
        return None
    cleaned = str(track).strip()
    return TRACK_ALIASES.get(cleaned, cleaned.replace("_", " "))


def build_guidance_plan(user: User, student: Student, db: Session) -> Dict:
    """Build a student guidance plan from current learning signals."""
    enrollments = db.query(Enrollment).filter(Enrollment.student_id == user.id).all()
    submissions = db.query(QuizSubmission).filter(QuizSubmission.student_id == student.id).all()
    lesson_progress = db.query(LessonProgress).filter(LessonProgress.student_id == user.id).all()
    attendance = db.query(Attendance).filter(Attendance.student_id == student.id).all()

    performance = _summarize_performance(submissions, db)
    activity = _summarize_activity(enrollments, lesson_progress, attendance)
    signals = build_learning_feature_vector(user, student, db)
    suggested_track = _suggest_track(student, performance, activity, signals)
    support = _support_level(performance, activity)
    next_steps = _next_steps(student, enrollments, performance, activity, suggested_track, support, db)
    course_matches = _course_matches(student, enrollments, suggested_track, db)

    return {
        "student": {
            "id": student.id,
            "name": student.name,
            "interest_track": student.interest_track,
            "predicted_track": student.predicted_track,
        },
        "guidance_summary": _summary_text(student, suggested_track, support, activity, performance),
        "suggested_track": suggested_track,
        "support_level": support,
        "learning_pattern": {
            "pace": activity["pace"],
            "consistency": activity["consistency"],
            "confidence": performance["confidence"],
            "best_signal": performance["best_signal"],
            "needs_support_in": performance["needs_support_in"],
        },
        "metrics": {
            "enrolled_courses": len(enrollments),
            "average_course_progress": activity["average_course_progress"],
            "lessons_started": activity["lessons_started"],
            "lessons_completed": activity["lessons_completed"],
            "quiz_attempts": performance["quiz_attempts"],
            "quiz_success_rate": performance["quiz_success_rate"],
            "attendance_rate": activity["attendance_rate"],
        },
        "next_steps": next_steps,
        "recommended_courses": course_matches,
        "model": {
            "used": suggested_track["source"] == "ml_model",
            "fallback_reason": suggested_track.get("fallback_reason"),
            "readiness": signals["readiness"],
            "evidence_count": signals["evidence_count"],
            "signals": signals,
        },
        "generated_at": datetime.utcnow().isoformat(),
    }


def _summarize_performance(submissions: List[QuizSubmission], db: Session) -> Dict:
    by_track = defaultdict(lambda: {"attempts": 0, "correct": 0, "score": 0})
    by_module = defaultdict(lambda: {"module_id": None, "module_name": "", "attempts": 0, "correct": 0})

    for submission in submissions:
        quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
        if not quiz or not quiz.lesson:
            continue
        lesson = quiz.lesson
        module = db.query(Module).filter(Module.id == lesson.module_id).first()
        course = db.query(Course).filter(Course.id == module.course_id).first() if module else None
        track = course.track_type if course else "General"

        by_track[track]["attempts"] += 1
        by_track[track]["correct"] += 1 if submission.is_correct else 0
        by_track[track]["score"] += submission.score or 0

        if module:
            by_module[module.id]["module_id"] = module.id
            by_module[module.id]["module_name"] = module.title
            by_module[module.id]["attempts"] += 1
            by_module[module.id]["correct"] += 1 if submission.is_correct else 0

    quiz_attempts = len(submissions)
    correct = sum(1 for item in submissions if item.is_correct)
    success_rate = round((correct / quiz_attempts) * 100, 1) if quiz_attempts else 0.0

    strongest_track = None
    weakest_module = None
    for track, stats in by_track.items():
        rate = stats["correct"] / stats["attempts"] if stats["attempts"] else 0
        if not strongest_track or rate > strongest_track["rate"]:
            strongest_track = {"track": track, "rate": rate}

    for stats in by_module.values():
        rate = stats["correct"] / stats["attempts"] if stats["attempts"] else 0
        if stats["attempts"] >= 2 and (not weakest_module or rate < weakest_module["rate"]):
            weakest_module = {**stats, "rate": rate}

    confidence = "new learner"
    if quiz_attempts >= 8 and success_rate >= 75:
        confidence = "growing confidence"
    elif quiz_attempts >= 5 and success_rate < 50:
        confidence = "needs reassurance"
    elif quiz_attempts >= 3:
        confidence = "building rhythm"

    return {
        "quiz_attempts": quiz_attempts,
        "quiz_success_rate": success_rate,
        "track_stats": dict(by_track),
        "best_signal": strongest_track["track"] if strongest_track else None,
        "needs_support_in": weakest_module["module_name"] if weakest_module else None,
        "weakest_module_id": weakest_module["module_id"] if weakest_module else None,
        "confidence": confidence,
    }


def _summarize_activity(enrollments: List[Enrollment], progress: List[LessonProgress], attendance: List[Attendance]) -> Dict:
    avg_progress = round(sum(e.progress_percentage or 0 for e in enrollments) / len(enrollments), 1) if enrollments else 0.0
    completed_lessons = sum(1 for item in progress if item.completed)
    started_lessons = len(progress)
    active_days = {item.started_at.date() for item in progress if item.started_at}

    attendance_rate = None
    if attendance:
        present = sum(1 for item in attendance if item.present)
        attendance_rate = round((present / len(attendance)) * 100, 1)

    pace = "getting started"
    if started_lessons >= 4 and avg_progress < 35:
        pace = "slow and steady"
    elif avg_progress >= 70:
        pace = "fast mover"
    elif avg_progress >= 35:
        pace = "steady"

    consistency = "not enough activity yet"
    if len(active_days) >= 4:
        consistency = "consistent"
    elif len(active_days) >= 2:
        consistency = "occasional"

    return {
        "average_course_progress": avg_progress,
        "lessons_started": started_lessons,
        "lessons_completed": completed_lessons,
        "attendance_rate": attendance_rate,
        "pace": pace,
        "consistency": consistency,
    }


def _suggest_track(student: Student, performance: Dict, activity: Dict, signals: Optional[Dict] = None) -> Dict:
    feature_scores = {
        "math_score": 50,
        "verbal_score": 50,
        "logic_score": 50,
        "creative_score": 50,
    }

    for track, stats in performance["track_stats"].items():
        feature = TRACK_FEATURES.get(track)
        if feature and stats["attempts"]:
            feature_scores[feature] = max(feature_scores[feature], round(stats["score"] / stats["attempts"]))

    confidence_level = min(1.0, max(0.25, performance["quiz_success_rate"] / 100 if performance["quiz_attempts"] else 0.35))
    attendance_rate = (activity["attendance_rate"] / 100) if activity["attendance_rate"] is not None else 0.75

    if performance["quiz_attempts"] >= 3:
        try:
            prediction = predict_interest_track(
                math_score=int(feature_scores["math_score"]),
                verbal_score=int(feature_scores["verbal_score"]),
                logic_score=int(feature_scores["logic_score"]),
                creative_score=int(feature_scores["creative_score"]),
                confidence_level=float(confidence_level),
                attendance_rate=float(attendance_rate),
                quiz_success_rate=float((signals or {}).get("quiz_success_rate", confidence_level)),
                lesson_completion_rate=float((signals or {}).get("lesson_completion_rate", 0.5)),
                learning_pace=float((signals or {}).get("learning_pace", 0.5)),
                consistency_score=float((signals or {}).get("consistency_score", attendance_rate)),
            )
            predicted_track = _canonical_track(prediction["predicted_track"]) or "Computer Basics"
            available_tracks = {
                item[0]
                for item in db.query(Course.track_type).distinct().all()
                if item[0]
            }
            if available_tracks and predicted_track not in available_tracks:
                fallback = _canonical_track(student.interest_track or performance["best_signal"] or student.predicted_track)
                if fallback in available_tracks:
                    return {
                        "track": fallback,
                        "confidence": 58,
                        "source": "interest_profile",
                        "fallback_reason": f"ML model predicted legacy track '{predicted_track}', but current courses use college streams",
                    }
            alternatives = {
                _canonical_track(track) or track: probability
                for track, probability in prediction.get("all_probabilities", {}).items()
            }
            return {
                "track": predicted_track,
                "confidence": round(prediction["probability"] * 100, 1),
                "source": "ml_model",
                "alternatives": alternatives,
            }
        except Exception as exc:
            fallback = _canonical_track(student.interest_track or performance["best_signal"] or student.predicted_track) or "Computer Basics"
            return {
                "track": fallback,
                "confidence": 55,
                "source": "rules",
                "fallback_reason": str(exc),
            }

    fallback = _canonical_track(student.interest_track or student.predicted_track or performance["best_signal"]) or "Computer Basics"
    return {
        "track": fallback,
        "confidence": 45 if performance["quiz_attempts"] == 0 else 60,
        "source": "interest_profile",
        "fallback_reason": "Not enough quiz history for the ML model yet",
    }


def _support_level(performance: Dict, activity: Dict) -> str:
    if performance["quiz_attempts"] >= 5 and performance["quiz_success_rate"] < 45:
        return "high"
    if activity["lessons_started"] >= 4 and activity["average_course_progress"] < 30:
        return "high"
    if performance["quiz_attempts"] < 3 or performance["quiz_success_rate"] < 65:
        return "medium"
    return "light"


def _next_steps(student: Student, enrollments: List[Enrollment], performance: Dict, activity: Dict, suggested_track: Dict, support: str, db: Session) -> List[Dict]:
    steps = []

    if support == "high":
        steps.append({
            "title": "Take one small lesson",
            "description": "Choose a short lesson and finish only that today. Small wins matter.",
            "type": "gentle_start",
            "priority": "high",
        })

    if performance["weakest_module_id"]:
        lesson = db.query(Lesson).filter(Lesson.module_id == performance["weakest_module_id"]).order_by(Lesson.id).first()
        steps.append({
            "title": f"Review {performance['needs_support_in']}",
            "description": "This topic looks shaky from quiz attempts. Review it before taking harder quizzes.",
            "type": "revision",
            "priority": "high",
            "lesson_id": lesson.id if lesson else None,
        })

    active = next((item for item in enrollments if not item.completed), None)
    if active:
        steps.append({
            "title": "Continue your current course",
            "description": "Stay with one path until it feels familiar. Jumping around makes learning harder.",
            "type": "continue_course",
            "priority": "medium",
            "course_id": active.course_id,
        })
    else:
        steps.append({
            "title": f"Start with {suggested_track['track']}",
            "description": "This matches your current interest signals. Begin with a beginner-friendly course.",
            "type": "start_track",
            "priority": "medium",
        })

    steps.append({
        "title": "Practice without pressure",
        "description": "Try 3 questions after learning. The goal is to notice patterns, not to be perfect.",
        "type": "practice",
        "priority": "medium" if support != "light" else "low",
    })

    return steps[:4]


def _course_matches(student: Student, enrollments: List[Enrollment], suggested_track: Dict, db: Session) -> List[Dict]:
    enrolled_ids = {item.course_id for item in enrollments}
    tracks = [
        _canonical_track(suggested_track["track"]),
        _canonical_track(student.interest_track),
        _canonical_track(student.predicted_track),
    ]
    tracks = [track for track in tracks if track]

    query = db.query(Course).filter(~Course.id.in_(enrolled_ids)) if enrolled_ids else db.query(Course)
    if tracks:
        courses = query.filter(Course.track_type.in_(tracks)).limit(5).all()
        if not courses:
            courses = query.order_by(Course.rating.desc(), Course.id.asc()).limit(5).all()
    else:
        courses = query.limit(5).all()

    return [
        {
            "course_id": course.id,
            "title": course.title,
            "track_type": course.track_type,
            "level": course.level,
            "reason": "Matches interest and learning pattern",
        }
        for course in courses
    ]


def _summary_text(student: Student, suggested_track: Dict, support: str, activity: Dict, performance: Dict) -> str:
    name = student.name or "This student"
    if support == "high":
        return f"{name} may need a slower, more encouraging path in {suggested_track['track']}. Focus on one small lesson, revision, and low-pressure practice."
    if performance["quiz_attempts"] == 0:
        return f"{name} is just starting. Use their interest in {suggested_track['track']} to choose a beginner course and collect learning signals."
    return f"{name} is showing a {activity['pace']} pace. Keep guiding them through {suggested_track['track']} with short practice and timely revision."
