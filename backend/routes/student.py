from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import Student, Enrollment, Course
from models.user import User
from routes.auth import get_current_user, require_admin
from schemas import StudentCreate, StudentResponse, StudentUpdate

router = APIRouter(
    prefix="/students",
    tags=["students"],
)

@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    """Create a new student"""
    db_student = Student(
        name=student.name,
        age=student.age,
        guardian_contact=student.guardian_contact,
        interest_track=student.interest_track,
        predicted_track=student.predicted_track,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student

@router.get("/", response_model=list[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all students with pagination"""
    students = db.query(Student).offset(skip).limit(limit).all()
    return students


@router.get("/admin/list")
def get_students_admin(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all student profiles with user email and enrollment counts."""
    students = db.query(Student).offset(skip).limit(limit).all()
    result = []
    for student in students:
        enrollment_count = 0
        if student.user_id:
            enrollment_count = db.query(Enrollment).filter(Enrollment.student_id == student.user_id).count()
        result.append({
            "id": student.id,
            "user_id": student.user_id,
            "name": student.name,
            "email": student.user.email if student.user else None,
            "age": student.age,
            "guardian_contact": student.guardian_contact,
            "interest_track": student.interest_track,
            "predicted_track": student.predicted_track,
            "enrollment_count": enrollment_count,
            "created_at": student.created_at.isoformat() if student.created_at else None,
        })
    return result


@router.get("/admin/{student_id}")
def get_student_admin(
    student_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get a student profile and enrollments for admin views."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    enrollments = []
    if student.user_id:
        rows = db.query(Enrollment).filter(Enrollment.student_id == student.user_id).all()
        for enrollment in rows:
            enrollments.append({
                "id": enrollment.id,
                "course_id": enrollment.course_id,
                "course_title": enrollment.course.title if enrollment.course else None,
                "progress_percentage": enrollment.progress_percentage,
                "completed": enrollment.completed,
                "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
            })

    return {
        "id": student.id,
        "user_id": student.user_id,
        "name": student.name,
        "email": student.user.email if student.user else None,
        "age": student.age,
        "guardian_contact": student.guardian_contact,
        "interest_track": student.interest_track,
        "predicted_track": student.predicted_track,
        "created_at": student.created_at.isoformat() if student.created_at else None,
        "enrollments": enrollments,
    }


@router.put("/admin/{student_id}", response_model=StudentResponse)
def update_student_admin(
    student_id: int,
    student_update: StudentUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update a student profile as admin."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    for field, value in student_update.model_dump(exclude_unset=True).items():
        setattr(student, field, value)

    db.commit()
    db.refresh(student)
    return student


@router.delete("/admin/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_admin(
    student_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a student profile and its user account if linked."""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    if student.user:
        db.delete(student.user)
    else:
        db.delete(student)
    db.commit()


@router.get("/profile/me")
def get_my_student_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get the current user's student profile."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    enrollments = db.query(Enrollment).filter(Enrollment.student_id == current_user.id).all()
    courses = []
    for enrollment in enrollments:
        course = enrollment.course
        courses.append({
            "course_id": enrollment.course_id,
            "course_title": course.title if course else None,
            "track_type": course.track_type if course else None,
            "level": course.level if course else None,
            "progress_percentage": enrollment.progress_percentage,
            "completed": enrollment.completed,
            "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None,
        })

    completed = sum(1 for enrollment in enrollments if enrollment.completed)
    in_progress = sum(1 for enrollment in enrollments if not enrollment.completed and enrollment.progress_percentage > 0)

    return {
        "id": student.id,
        "user_id": student.user_id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "name": student.name,
        "age": student.age,
        "guardian_contact": student.guardian_contact,
        "interest_track": student.interest_track,
        "predicted_track": student.predicted_track,
        "created_at": student.created_at.isoformat() if student.created_at else None,
        "stats": {
            "total_enrolled": len(enrollments),
            "completed": completed,
            "in_progress": in_progress,
            "avg_quiz_score": 0,
            "total_quizzes_taken": 0,
        },
        "courses": courses,
    }


@router.put("/profile/me", response_model=StudentResponse)
def update_my_student_profile(
    student_update: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update the current user's student profile."""
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student profile not found")

    for field in ("name", "age", "guardian_contact", "interest_track", "predicted_track"):
        if field in student_update:
            setattr(student, field, student_update[field])

    if student_update.get("email"):
        existing = db.query(User).filter(User.email == student_update["email"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
        current_user.email = student_update["email"]

    db.commit()
    db.refresh(student)
    return student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific student by ID"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found"
        )
    return student
