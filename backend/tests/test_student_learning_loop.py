from models import Badge, Course, Enrollment, Lesson, LessonProgress, Module, Quiz, QuizSubmission, Student, StudentBadge
from models.badge import BadgeConditionType
from models.quiz import AnswerChoice
from tests.conftest import get_auth_header


def test_my_achievements_returns_badges(client, test_db, student_user, student_token):
    student = test_db.query(Student).filter_by(user_id=student_user.id).first()
    badge = Badge(
        name="Careful Starter",
        description="Started learning with care.",
        condition_type=BadgeConditionType.FIRST_LESSON,
        color="success",
        points=15,
    )
    test_db.add(badge)
    test_db.commit()
    test_db.add(StudentBadge(student_id=student.id, badge_id=badge.id))
    test_db.commit()

    response = client.get("/api/badges/my-achievements", headers=get_auth_header(student_token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_badges"] == 1
    assert data["total_points"] == 15
    assert data["badges"][0]["name"] == "Careful Starter"


def test_course_progress_uses_total_lessons_as_denominator(client, test_db, student_user, student_token):
    course = Course(title="Balanced Practice", track_type="Mathematics", level="Intermediate")
    test_db.add(course)
    test_db.commit()
    module = Module(course_id=course.id, title="Practice Module", order_number=1)
    test_db.add(module)
    test_db.commit()
    lessons = [
        Lesson(module_id=module.id, title=f"Lesson {index}", content="Practice", duration_minutes=10)
        for index in range(1, 5)
    ]
    test_db.add_all(lessons)
    test_db.commit()
    test_db.add(Enrollment(student_id=student_user.id, course_id=course.id, progress_percentage=25))
    test_db.add(LessonProgress(student_id=student_user.id, lesson_id=lessons[0].id, completed=True))
    test_db.commit()

    response = client.get(f"/api/lessons/course/{course.id}/progress", headers=get_auth_header(student_token))

    assert response.status_code == 200
    data = response.json()
    assert data["total_lessons_completed"] == 1
    assert data["overall_completion_percentage"] == 25
    assert data["completed_lesson_ids"] == [lessons[0].id]


def test_predict_my_track_uses_learning_signals(client, test_db, student_user, student_token):
    student = test_db.query(Student).filter_by(user_id=student_user.id).first()
    course = Course(title="Signal Course", track_type="Mathematics", level="Intermediate")
    test_db.add(course)
    test_db.commit()
    module = Module(course_id=course.id, title="Numbers", order_number=1)
    test_db.add(module)
    test_db.commit()
    lesson = Lesson(module_id=module.id, title="Patterns", content="Practice", duration_minutes=10)
    test_db.add(lesson)
    test_db.commit()
    quiz = Quiz(
        lesson_id=lesson.id,
        question="What checks an answer?",
        option_a="Substitution",
        option_b="Guessing",
        option_c="Skipping",
        option_d="Copying",
        correct_answer=AnswerChoice.A,
    )
    test_db.add(quiz)
    test_db.add(Enrollment(student_id=student_user.id, course_id=course.id, progress_percentage=50))
    test_db.add(LessonProgress(student_id=student_user.id, lesson_id=lesson.id, completed=True))
    test_db.commit()
    test_db.add(QuizSubmission(student_id=student.id, quiz_id=quiz.id, selected_answer=AnswerChoice.A, score=100, is_correct=True))
    test_db.commit()

    response = client.get("/api/predict/my-track", headers=get_auth_header(student_token))

    assert response.status_code == 200
    data = response.json()
    assert "predicted_track" in data
    assert "_" not in data["predicted_track"]
    assert data["signals"]["quiz_attempts"] == 1
    assert data["signals"]["lessons_completed"] == 1
