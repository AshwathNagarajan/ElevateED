"""
Analytics service for calculating course and quiz statistics.
Provides clean interfaces for analytics calculations used across admin and mentor dashboards.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Course, Enrollment, Quiz, QuizSubmission, Lesson
from schemas.analytics import (
    CourseCompletionStats,
    QuizScoreStats,
)
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# COURSE COMPLETION ANALYTICS
# ============================================================================

def calculate_course_completion_rate(db: Session) -> Dict:
    """
    Calculate course completion rate statistics for all courses.
    
    ✅ OPTIMIZATION: Uses single SQL aggregation query instead of N+1 pattern.
    Before: 1 query for courses + N queries (one per course) for enrollments
    After: 1 single aggregation query
    
    Returns:
        Dict with:
        - total_courses: Number of courses in system
        - total_enrollments: Total enrollments across all courses
        - overall_completion_rate: Overall percentage
        - courses: List of CourseCompletionStats
    """
    try:
        # ✅ Single aggregation query using SQL instead of Python loops
        stats_query = db.query(
            Course.id,
            Course.title,
            func.count(Enrollment.id).label('total_enrollments'),
            func.sum(
                func.cast(Enrollment.completed, func.Integer())
            ).label('completed_count'),
            func.sum(
                func.case(
                    (func.and_(
                        Enrollment.completed == False,
                        (Enrollment.progress_percentage or 0) > 0
                    ), 1),
                    else_=0
                )
            ).label('in_progress_count'),
            func.avg(Enrollment.progress_percentage or 0).label('average_progress')
        ).outerjoin(
            Enrollment, Course.id == Enrollment.course_id
        ).group_by(
            Course.id, Course.title
        ).all()
        
        if not stats_query:
            return {
                "total_courses": 0,
                "total_enrollments": 0,
                "overall_completion_rate": 0.0,
                "courses": []
            }
        
        course_stats = []
        total_enrollments = 0
        total_completed = 0
        
        for course_id, title, total, completed, in_progress, avg_progress in stats_query:
            total_enrollments += (total or 0)
            total_completed += (completed or 0)
            
            completion_rate = ((completed or 0) / (total or 1) * 100) if total else 0.0
            
            course_stats.append(CourseCompletionStats(
                course_id=course_id,
                course_title=title or "Untitled",
                total_enrollments=total or 0,
                completed_count=completed or 0,
                in_progress_count=in_progress or 0,
                not_started_count=(total or 0) - (completed or 0) - (in_progress or 0),
                completion_rate=round(completion_rate, 2),
                average_progress=round(float(avg_progress or 0), 2)
            ))
        
        overall_completion_rate = (total_completed / total_enrollments * 100) if total_enrollments > 0 else 0.0
        
        return {
            "total_courses": len(course_stats),
            "total_enrollments": total_enrollments,
            "overall_completion_rate": round(overall_completion_rate, 2),
            "courses": course_stats
        }
    except Exception as e:
        logger.error(f"Error calculating course completion rate: {str(e)}")
        return {
            "total_courses": 0,
            "total_enrollments": 0,
            "overall_completion_rate": 0.0,
            "courses": []
        }


def _calculate_single_course_stats(course: Course, db: Session) -> Tuple[CourseCompletionStats, int, int]:
    """
    Calculate statistics for a single course.
    
    Returns:
        Tuple of (CourseCompletionStats, total_enrollments, completed_count)
    """
    enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
    total_course_enrollments = len(enrollments)
    
    if total_course_enrollments == 0:
        return CourseCompletionStats(
            course_id=course.id,
            course_title=course.title or "Untitled",
            total_enrollments=0,
            completed_count=0,
            in_progress_count=0,
            not_started_count=0,
            completion_rate=0.0,
            average_progress=0.0
        ), 0, 0
    
    # Count students by status
    completed = sum(1 for e in enrollments if e.completed)
    in_progress = sum(1 for e in enrollments if not e.completed and (e.progress_percentage or 0) > 0)
    not_started = sum(1 for e in enrollments if (e.progress_percentage or 0) == 0 and not e.completed)
    
    # Calculate rates
    completion_rate = (completed / total_course_enrollments * 100) if total_course_enrollments > 0 else 0.0
    average_progress = sum(e.progress_percentage or 0 for e in enrollments) / total_course_enrollments
    
    stats = CourseCompletionStats(
        course_id=course.id,
        course_title=course.title or "Untitled",
        total_enrollments=total_course_enrollments,
        completed_count=completed,
        in_progress_count=in_progress,
        not_started_count=not_started,
        completion_rate=round(completion_rate, 2),
        average_progress=round(average_progress, 2)
    )
    
    return stats, total_course_enrollments, completed


# ============================================================================
# QUIZ SCORE ANALYTICS
# ============================================================================

def calculate_average_quiz_score(db: Session) -> Dict:
    """
    Calculate average quiz score statistics for all quizzes.
    
    ✅ OPTIMIZATION: Uses single SQL aggregation query instead of N+1 pattern.
    Before: 1 query for quizzes + N queries (one per quiz) for submissions
    After: 1 single aggregation query
    
    Returns:
        Dict with:
        - total_quizzes: Number of quizzes
        - total_attempts: Total quiz attempts
        - overall_average_score: Overall average
        - overall_success_rate: Overall success percentage
        - quizzes: List of QuizScoreStats
    """
    try:
        # ✅ Single aggregation query using SQL instead of Python loops
        stats_query = db.query(
            Quiz.id,
            Quiz.question,
            Lesson.title.label('lesson_title'),
            func.count(QuizSubmission.id).label('total_attempts'),
            func.sum(
                func.cast(QuizSubmission.is_correct, func.Integer())
            ).label('correct_count'),
            func.avg(QuizSubmission.score).label('average_score')
        ).outerjoin(
            Lesson, Quiz.lesson_id == Lesson.id
        ).outerjoin(
            QuizSubmission, Quiz.id == QuizSubmission.quiz_id
        ).group_by(
            Quiz.id, Quiz.question, Lesson.title
        ).all()
        
        if not stats_query:
            return {
                "total_quizzes": 0,
                "total_attempts": 0,
                "overall_average_score": 0.0,
                "overall_success_rate": 0.0,
                "quizzes": []
            }
        
        quiz_stats = []
        total_attempts = 0
        total_correct = 0
        all_scores = []
        
        for quiz_id, question, lesson_title, attempts, correct, avg_score in stats_query:
            total_attempts += (attempts or 0)
            total_correct += (correct or 0)
            if avg_score:
                all_scores.append(avg_score)
            
            success_rate = ((correct or 0) / (attempts or 1) * 100) if attempts else 0.0
            
            quiz_stats.append(QuizScoreStats(
                quiz_id=quiz_id,
                quiz_question=question or "",
                lesson_title=lesson_title,
                total_attempts=attempts or 0,
                correct_count=correct or 0,
                average_score=round(float(avg_score or 0), 2),
                success_rate=round(success_rate, 2)
            ))
        
        overall_average = sum(all_scores) / len(all_scores) if all_scores else 0.0
        overall_success = (total_correct / total_attempts * 100) if total_attempts > 0 else 0.0
        
        return {
            "total_quizzes": len(quiz_stats),
            "total_attempts": total_attempts,
            "overall_average_score": round(overall_average, 2),
            "overall_success_rate": round(overall_success, 2),
            "quizzes": quiz_stats
        }
    except Exception as e:
        logger.error(f"Error calculating average quiz score: {str(e)}")
        return {
            "total_quizzes": 0,
            "total_attempts": 0,
            "overall_average_score": 0.0,
            "overall_success_rate": 0.0,
            "quizzes": []
        }


def _calculate_single_quiz_stats(quiz: Quiz, db: Session) -> Tuple[QuizScoreStats, int, int]:
    """
    Calculate statistics for a single quiz.
    
    Returns:
        Tuple of (QuizScoreStats, total_attempts, correct_count)
    """
    submissions = db.query(QuizSubmission).filter(QuizSubmission.quiz_id == quiz.id).all()
    
    quiz_attempts = len(submissions)
    quiz_correct = sum(1 for s in submissions if s.is_correct)
    quiz_scores = [s.score or 0 for s in submissions]
    
    avg_score = sum(quiz_scores) / len(quiz_scores) if quiz_scores else 0.0
    success_rate = (quiz_correct / quiz_attempts * 100) if quiz_attempts > 0 else 0.0
    
    lesson_title = quiz.lesson.title if quiz.lesson else None
    
    stats = QuizScoreStats(
        quiz_id=quiz.id,
        quiz_question=quiz.question or "",
        lesson_title=lesson_title,
        total_attempts=quiz_attempts,
        correct_count=quiz_correct,
        average_score=round(avg_score, 2),
        success_rate=round(success_rate, 2)
    )
    
    return stats, quiz_attempts, quiz_correct


# ============================================================================
# ACTIVE LEARNERS ANALYTICS
# ============================================================================

def calculate_active_learners(db: Session, days: int = 7) -> Dict:
    """
    Calculate active learners statistics.
    
    Args:
        db: Database session
        days: Number of days to look back (default 7)
    
    Returns:
        Dict with active learner metrics
    """
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import and_
        
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Count unique students with quiz submissions in the period
        active_students = db.query(func.count(func.distinct(QuizSubmission.student_id))).filter(
            QuizSubmission.created_at >= start_date
        ).scalar() or 0
        
        # Get daily active counts
        daily_stats = db.query(
            func.date(QuizSubmission.created_at).label("date"),
            func.count(func.distinct(QuizSubmission.student_id)).label("active_count")
        ).filter(
            QuizSubmission.created_at >= start_date
        ).group_by(
            func.date(QuizSubmission.created_at)
        ).all()
        
        daily_active_users = [
            {
                "date": str(stat[0]),
                "active_count": stat[1]
            }
            for stat in daily_stats
        ]
        
        return {
            "period_days": days,
            "total_active_students": active_students,
            "daily_active_users": daily_active_users
        }
    except Exception as e:
        logger.error(f"Error calculating active learners: {str(e)}")
        return {
            "period_days": days,
            "total_active_students": 0,
            "daily_active_users": []
        }


# ============================================================================
# MENTOR DASHBOARD ANALYTICS
# ============================================================================

def calculate_mentor_dashboard_stats(mentor_id: int, db: Session) -> Dict:
    """
    Calculate comprehensive stats for mentor's dashboard.
    
    Args:
        mentor_id: ID of the mentor (user_id)
        db: Database session
    
    Returns:
        Dict with mentor dashboard statistics
    """
    try:
        courses = db.query(Course).filter(Course.mentor_id == mentor_id).all()
        
        if not courses:
            return {
                "total_courses": 0,
                "total_students": 0,
                "overall_completion_rate": 0.0,
                "overall_avg_quiz_score": 0.0,
                "courses": []
            }
        
        course_stats = []
        total_students = 0
        total_completed = 0
        total_enrollments = 0
        all_quiz_scores = []
        
        for course in courses:
            # Get course stats
            enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
            total_course_enrollments = len(enrollments)
            
            completed = sum(1 for e in enrollments if e.completed)
            in_progress = sum(1 for e in enrollments if not e.completed and (e.progress_percentage or 0) > 0)
            not_started = sum(1 for e in enrollments if (e.progress_percentage or 0) == 0 and not e.completed)
            
            completion_rate = (completed / total_course_enrollments * 100) if total_course_enrollments > 0 else 0.0
            average_progress = sum(e.progress_percentage or 0 for e in enrollments) / total_course_enrollments if total_course_enrollments > 0 else 0.0
            
            # Get quiz stats for this course
            course_quiz_scores = []
            total_quizzes = db.query(func.count(Quiz.id)).join(
                Lesson, Lesson.id == Quiz.lesson_id
            ).join(
                Module, Module.id == Lesson.module_id
            ).filter(Module.course_id == course.id).scalar() or 0
            
            submissions = db.query(QuizSubmission).join(
                Quiz, Quiz.id == QuizSubmission.quiz_id
            ).join(
                Lesson, Lesson.id == Quiz.lesson_id
            ).join(
                Module, Module.id == Lesson.module_id
            ).filter(Module.course_id == course.id).all()
            
            if submissions:
                course_quiz_scores = [s.score or 0 for s in submissions]
                all_quiz_scores.extend(course_quiz_scores)
            
            avg_quiz = sum(course_quiz_scores) / len(course_quiz_scores) if course_quiz_scores else 0.0
            
            course_stats.append({
                "course_id": course.id,
                "course_title": course.title or "Untitled",
                "total_enrolled": total_course_enrollments,
                "completed": completed,
                "in_progress": in_progress,
                "not_started": not_started,
                "completion_rate": round(completion_rate, 2),
                "avg_progress": round(average_progress, 2),
                "total_quizzes": total_quizzes,
                "avg_quiz_score": round(avg_quiz, 2)
            })
            
            total_students += total_course_enrollments
            total_completed += completed
            total_enrollments += total_course_enrollments
        
        # Calculate overall stats
        overall_completion = (total_completed / total_enrollments * 100) if total_enrollments > 0 else 0.0
        overall_avg_quiz = sum(all_quiz_scores) / len(all_quiz_scores) if all_quiz_scores else 0.0
        
        return {
            "total_courses": len(courses),
            "total_students": total_students,
            "overall_completion_rate": round(overall_completion, 2),
            "overall_avg_quiz_score": round(overall_avg_quiz, 2),
            "courses": course_stats
        }
    except Exception as e:
        logger.error(f"Error calculating mentor dashboard stats: {str(e)}")
        return {
            "total_courses": 0,
            "total_students": 0,
            "overall_completion_rate": 0.0,
            "overall_avg_quiz_score": 0.0,
            "courses": []
        }
