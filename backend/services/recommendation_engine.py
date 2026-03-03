from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from models import Quiz, QuizSubmission, Lesson, Module, Course, Student
from typing import List, Dict, Optional
from datetime import datetime


def analyze_student_performance(student_id: int, db: Session) -> List[Dict]:
    """
    Analyze student's quiz performance and generate recommendations.
    
    Rules:
    - If student fails more than 2 quizzes in a module → recommend revision lesson
    - If high performance (≥80% success rate) in a module → recommend next level
    - If low performance (<50% success rate) → recommend foundational review
    
    Args:
        student_id: ID of the student to analyze
        db: Database session
        
    Returns:
        List of recommendation dictionaries with:
        - type: "revision", "next_level", "foundational_review"
        - module_id: Module being recommended for
        - module_name: Name of the module
        - message: Human-readable recommendation message
        - reason: Explanation for the recommendation
        - score: Student's score percentage in module
        - failed_count: Number of failed quizzes (for revision recommendations)
    """
    
    # Verify student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return []
    
    recommendations = []
    
    # Get all quiz submissions for the student grouped by module
    submissions = db.query(
        QuizSubmission,
        Quiz,
        Lesson,
        Module
    ).join(
        Quiz, QuizSubmission.quiz_id == Quiz.id
    ).join(
        Lesson, Quiz.lesson_id == Lesson.id
    ).join(
        Module, Lesson.module_id == Module.id
    ).filter(
        QuizSubmission.student_id == student_id
    ).all()
    
    if not submissions:
        return recommendations
    
    # Organize submissions by module
    module_stats = {}
    
    for submission, quiz, lesson, module in submissions:
        module_id = module.id
        
        if module_id not in module_stats:
            module_stats[module_id] = {
                "module_name": module.title,
                "total_quizzes": 0,
                "passed_quizzes": 0,
                "failed_quizzes": 0,
                "total_score": 0,
            }
        
        module_stats[module_id]["total_quizzes"] += 1
        module_stats[module_id]["total_score"] += submission.score
        
        if submission.is_correct:
            module_stats[module_id]["passed_quizzes"] += 1
        else:
            module_stats[module_id]["failed_quizzes"] += 1
    
    # Generate recommendations based on performance
    for module_id, stats in module_stats.items():
        if stats["total_quizzes"] == 0:
            continue
        
        success_percentage = (stats["passed_quizzes"] / stats["total_quizzes"]) * 100
        average_score = stats["total_score"] / stats["total_quizzes"]
        
        # Rule 1: If more than 2 failures in a module → recommend revision
        if stats["failed_quizzes"] > 2:
            recommendations.append({
                "type": "revision",
                "module_id": module_id,
                "module_name": stats["module_name"],
                "message": f"Consider reviewing {stats['module_name']}. You had {stats['failed_quizzes']} quiz failures.",
                "reason": "Multiple quiz failures detected",
                "score": round(success_percentage, 2),
                "failed_count": stats["failed_quizzes"],
                "generated_at": datetime.utcnow().isoformat()
            })
        
        # Rule 2: High performance (≥80%) → recommend next level
        elif success_percentage >= 80:
            recommendations.append({
                "type": "next_level",
                "module_id": module_id,
                "module_name": stats["module_name"],
                "message": f"Great job in {stats['module_name']}! You're ready for the next level.",
                "reason": "High performance detected",
                "score": round(success_percentage, 2),
                "passed_count": stats["passed_quizzes"],
                "generated_at": datetime.utcnow().isoformat()
            })
        
        # Rule 3: Low performance (<50%) → recommend foundational review
        elif success_percentage < 50:
            recommendations.append({
                "type": "foundational_review",
                "module_id": module_id,
                "module_name": stats["module_name"],
                "message": f"Let's strengthen your fundamentals in {stats['module_name']}. Review the foundational concepts.",
                "reason": "Low performance detected",
                "score": round(success_percentage, 2),
                "failed_count": stats["failed_quizzes"],
                "generated_at": datetime.utcnow().isoformat()
            })
    
    return recommendations


def get_student_quiz_statistics(student_id: int, db: Session) -> Dict:
    """
    Get comprehensive quiz statistics for a student.
    
    Args:
        student_id: ID of the student
        db: Database session
        
    Returns:
        Dictionary with overall and per-module statistics
    """
    
    # Get all quiz submissions for the student
    submissions = db.query(QuizSubmission).filter(
        QuizSubmission.student_id == student_id
    ).all()
    
    if not submissions:
        return {
            "total_quizzes": 0,
            "passed": 0,
            "failed": 0,
            "success_percentage": 0,
            "average_score": 0,
            "module_stats": []
        }
    
    # Overall statistics
    total_quizzes = len(submissions)
    passed = sum(1 for s in submissions if s.is_correct)
    failed = total_quizzes - passed
    success_percentage = (passed / total_quizzes * 100) if total_quizzes > 0 else 0
    average_score = sum(s.score for s in submissions) / total_quizzes if total_quizzes > 0 else 0
    
    # Per-module statistics
    submissions_with_module = db.query(
        QuizSubmission,
        Quiz,
        Lesson,
        Module
    ).join(
        Quiz, QuizSubmission.quiz_id == Quiz.id
    ).join(
        Lesson, Quiz.lesson_id == Lesson.id
    ).join(
        Module, Lesson.module_id == Module.id
    ).filter(
        QuizSubmission.student_id == student_id
    ).all()
    
    module_stats = {}
    for submission, quiz, lesson, module in submissions_with_module:
        module_id = module.id
        if module_id not in module_stats:
            module_stats[module_id] = {
                "module_id": module.id,
                "module_name": module.title,
                "total": 0,
                "passed": 0,
                "failed": 0,
                "success_percentage": 0,
                "average_score": 0,
            }
        
        module_stats[module_id]["total"] += 1
        if submission.is_correct:
            module_stats[module_id]["passed"] += 1
        else:
            module_stats[module_id]["failed"] += 1
    
    # Calculate percentages for each module
    for module_id in module_stats:
        total = module_stats[module_id]["total"]
        passed = module_stats[module_id]["passed"]
        if total > 0:
            module_stats[module_id]["success_percentage"] = (passed / total) * 100
            # Get average score for module
            module_submissions = [s for s in submissions if db.query(Quiz, Lesson, Module).join(
                Lesson, Quiz.lesson_id == Lesson.id
            ).join(
                Module, Lesson.module_id == Module.id
            ).filter(Quiz.id == s.quiz_id).first()]
            
            module_score_sum = sum(
                s.score for s in submissions_with_module 
                if s[3].id == module_id
            )
            module_stats[module_id]["average_score"] = module_score_sum / total if total > 0 else 0
    
    return {
        "total_quizzes": total_quizzes,
        "passed": passed,
        "failed": failed,
        "success_percentage": round(success_percentage, 2),
        "average_score": round(average_score, 2),
        "module_stats": list(module_stats.values())
    }


def unlock_next_level(student_id: int, current_module_id: int, db: Session) -> Optional[Dict]:
    """
    Check if student qualifies to unlock the next level.
    
    Requirements:
    - Student must have ≥80% success rate in current module
    - Must have completed at least 5 quizzes
    
    Args:
        student_id: ID of the student
        current_module_id: ID of the current module
        db: Database session
        
    Returns:
        Dictionary with next module info if unlocked, None otherwise
    """
    
    # Get current module and its course
    current_module = db.query(Module).filter(Module.id == current_module_id).first()
    if not current_module:
        return None
    
    # Get student's performance in current module
    submissions = db.query(
        QuizSubmission,
        Quiz
    ).join(
        Quiz, QuizSubmission.quiz_id == Quiz.id
    ).join(
        Lesson, Quiz.lesson_id == Lesson.id
    ).filter(
        and_(
            QuizSubmission.student_id == student_id,
            Lesson.module_id == current_module_id
        )
    ).all()
    
    if len(submissions) < 5:
        return {
            "unlocked": False,
            "reason": f"Need at least 5 quiz attempts (currently at {len(submissions)})"
        }
    
    passed = sum(1 for s in submissions if s[0].is_correct)
    success_rate = (passed / len(submissions)) * 100
    
    if success_rate < 80:
        return {
            "unlocked": False,
            "reason": f"Need ≥80% success rate (currently at {success_rate:.1f}%)"
        }
    
    # Get next module in same course
    next_module = db.query(Module).filter(
        and_(
            Module.course_id == current_module.course_id,
            Module.order_number > current_module.order_number
        )
    ).order_by(Module.order_number).first()
    
    if not next_module:
        return {
            "unlocked": True,
            "message": "Congratulations! You've completed all modules in this course!",
            "next_module": None
        }
    
    return {
        "unlocked": True,
        "message": f"Unlocked: {next_module.title}",
        "next_module": {
            "id": next_module.id,
            "title": next_module.title,
            "order": next_module.order_number
        }
    }
