from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import Course, Enrollment
from models.user import User, RoleEnum
from models.mentor import Mentor
from routes.auth import get_current_user, require_mentor, require_admin
from schemas.course import CourseResponse
from schemas.auth import TokenPairResponse
from schemas.mentor import MentorCreate, MentorResponse
from core.security import TokenManager
from services.auth import hash_password
from typing import List

router = APIRouter(
    prefix="/mentors",
    tags=["mentors"],
)


@router.get("/", response_model=List[MentorResponse])
def get_all_mentors(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Get all mentors (admin only).
    """
    mentors = db.query(Mentor).offset(skip).limit(limit).all()
    return mentors


@router.get("/admin/list")
def get_mentors_admin(
    skip: int = 0,
    limit: int = 200,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Get all mentors with email and course count (admin only)"""
    mentors = db.query(Mentor).offset(skip).limit(limit).all()
    result = []
    for m in mentors:
        course_count = db.query(Course).filter(Course.mentor_id == m.user_id).count()
        result.append({
            "id": m.id,
            "user_id": m.user_id,
            "name": m.name,
            "email": m.user.email if m.user else None,
            "phone": m.phone,
            "qualification": m.qualification,
            "specialization": m.specialization,
            "experience_years": m.experience_years,
            "bio": m.bio,
            "linkedin_url": m.linkedin_url,
            "profile_image_url": m.profile_image_url,
            "course_count": course_count,
            "created_at": m.created_at.isoformat() if m.created_at else None,
        })
    return result


@router.put("/admin/{mentor_id}")
def update_mentor_admin(
    mentor_id: int,
    data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Update mentor details (admin only)"""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    for field in ("name", "phone", "qualification", "specialization", "experience_years", "bio", "linkedin_url"):
        if field in data:
            setattr(mentor, field, data[field])
    db.commit()
    db.refresh(mentor)
    return {"success": True, "id": mentor.id}


@router.delete("/admin/{mentor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mentor_admin(
    mentor_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Delete a mentor and their user account (admin only)"""
    mentor = db.query(Mentor).filter(Mentor.id == mentor_id).first()
    if not mentor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Mentor not found")
    if mentor.user_id:
        user = db.query(User).filter(User.id == mentor.user_id).first()
        if user:
            db.delete(user)  # cascades to mentor
        else:
            db.delete(mentor)
    else:
        db.delete(mentor)
    db.commit()
    return None


@router.post("/register", response_model=TokenPairResponse, status_code=status.HTTP_201_CREATED)
def register_mentor(
    user: MentorCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new mentor account.
    
    Creates a user account with mentor role.
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new mentor user
    db_user = User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hash_password(user.password),
        role=RoleEnum.MENTOR
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    mentor = Mentor(
        user_id=db_user.id,
        name=user.name or user.full_name,
        phone=user.phone,
        qualification=user.qualification,
        specialization=user.specialization,
        experience_years=user.experience_years,
        bio=user.bio,
        linkedin_url=user.linkedin_url,
    )
    db.add(mentor)
    db.commit()
    
    return {
        "access_token": TokenManager.create_access_token(db_user.id, RoleEnum.MENTOR.value),
        "refresh_token": TokenManager.create_refresh_token(db_user.id),
        "token_type": "bearer",
        "expires_in_minutes": TokenManager.ACCESS_TOKEN_EXPIRE_MINUTES,
    }


@router.get("/my-courses", response_model=List[CourseResponse])
def get_mentor_courses(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mentor)
):
    """
    Get all courses assigned to the currently logged-in mentor.
    
    Returns only courses where the mentor_id matches the current user's ID.
    """
    courses = db.query(Course).filter(Course.mentor_id == current_user.id).all()
    return courses


@router.get("/courses/{course_id}/students")
def get_mentor_course_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mentor)
):
    """
    Get all students enrolled in a mentor's course.
    
    Only accessible by the course's assigned mentor or an admin.
    """
    # Verify course belongs to mentor (or user is admin)
    role_value = current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role)
    
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    # Check if mentor owns this course or is admin
    if course.mentor_id != current_user.id and role_value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this course"
        )
    
    # Get all enrollments with student info
    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id
    ).all()
    
    students = []
    for enrollment in enrollments:
        if enrollment.student:
            students.append({
                "enrollment_id": enrollment.id,
                "student_id": enrollment.student.id,
                "student_name": enrollment.student.full_name,
                "student_email": enrollment.student.email,
                "progress_percentage": enrollment.progress_percentage or 0.0,
                "completed": enrollment.completed or False,
                "enrolled_at": enrollment.enrolled_at.isoformat() if enrollment.enrolled_at else None
            })
    
    return {
        "course_id": course_id,
        "course_title": course.title,
        "total_students": len(students),
        "students": students
    }


@router.get("/profile/me")
def get_mentor_profile_me(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mentor)
):
    """Get the logged-in mentor's full profile with stats and course list"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()

    courses = db.query(Course).filter(Course.mentor_id == current_user.id).all()

    courses_data = []
    total_students = 0
    for course in courses:
        enrollments = db.query(Enrollment).filter(Enrollment.course_id == course.id).all()
        completed = sum(1 for e in enrollments if e.completed)
        in_progress = sum(1 for e in enrollments if not e.completed and e.progress_percentage and e.progress_percentage > 0)
        avg_prog = round(sum(e.progress_percentage or 0 for e in enrollments) / len(enrollments), 1) if enrollments else 0
        total_students += len(enrollments)
        courses_data.append({
            "course_id": course.id,
            "course_title": course.title,
            "track_type": course.track_type,
            "level": course.level,
            "total_enrolled": len(enrollments),
            "completed": completed,
            "in_progress": in_progress,
            "avg_progress": avg_prog,
        })

    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "id": mentor.id if mentor else None,
        "name": mentor.name if mentor else current_user.full_name,
        "phone": mentor.phone if mentor else None,
        "qualification": mentor.qualification if mentor else None,
        "specialization": mentor.specialization if mentor else None,
        "experience_years": mentor.experience_years if mentor else None,
        "bio": mentor.bio if mentor else None,
        "linkedin_url": mentor.linkedin_url if mentor else None,
        "profile_image_url": mentor.profile_image_url if mentor else None,
        "created_at": mentor.created_at.isoformat() if mentor and mentor.created_at else None,
        "stats": {
            "total_courses": len(courses),
            "total_students": total_students,
        },
        "courses": courses_data,
    }


@router.put("/profile/me")
def update_mentor_profile_me(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mentor)
):
    """Update the logged-in mentor's own profile"""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    if not mentor:
        raise HTTPException(status_code=404, detail="Mentor profile not found")

    allowed = {"name", "phone", "qualification", "specialization", "experience_years", "bio", "linkedin_url"}
    for field in allowed:
        if field in data:
            setattr(mentor, field, data[field])

    if "email" in data and data["email"]:
        existing = db.query(User).filter(User.email == data["email"], User.id != current_user.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        current_user.email = data["email"]

    db.commit()
    db.refresh(mentor)
    return {"success": True}


@router.get("/profile")
def get_mentor_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_mentor)
):
    """Get the current mentor's profile information (legacy endpoint)."""
    mentor = db.query(Mentor).filter(Mentor.user_id == current_user.id).first()
    course_count = db.query(Course).filter(Course.mentor_id == current_user.id).count()

    # Get total students across all mentor's courses
    total_students = db.query(Enrollment).join(
        Course, Enrollment.course_id == Course.id
    ).filter(Course.mentor_id == current_user.id).count()
    
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role.value if hasattr(current_user.role, 'value') else str(current_user.role),
        "qualification": mentor.qualification if mentor else None,
        "specialization": mentor.specialization if mentor else None,
        "experience_years": mentor.experience_years if mentor else None,
        "bio": mentor.bio if mentor else None,
        "total_courses": course_count,
        "total_students": total_students
    }
