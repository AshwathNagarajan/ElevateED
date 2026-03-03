from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from typing import Optional
from database import get_db
from models import Course, Module, Lesson
from models.user import User
from schemas.course import (
    CourseCreate,
    CourseResponse,
    CourseDetailResponse,
    CourseUpdate,
    ModuleCreate,
    ModuleResponse,
    LessonCreate,
    LessonResponse,
)
from routes.auth import get_current_user, require_admin

router = APIRouter(
    prefix="/courses",
    tags=["courses"],
)


# ==================== COURSE ENDPOINTS ====================

@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new course (admin only).
    
    Requires admin role to create courses.
    """
    db_course = Course(
        title=course.title,
        description=course.description,
        track_type=course.track_type,
        level=course.level,
    )
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


@router.get("/", response_model=dict)
def get_courses(
    skip: int = 0,
    limit: int = 20,
    track_type: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all courses with pagination and filtering.
    
    Query Parameters:
    - **skip**: Number of courses to skip (default: 0)
    - **limit**: Maximum number of courses to return (default: 20, max: 100)
    - **track_type**: Filter by track type (e.g., 'Math', 'Science', 'Language')
    - **level**: Filter by difficulty level (e.g., 'Beginner', 'Intermediate', 'Advanced')
    
    Returns paginated response with:
    - skip, limit: Pagination parameters
    - total: Total courses matching filters
    - count: Number of courses in this response
    - page: Current page number (1-indexed)
    - pages: Total number of pages
    - filters: Applied filters
    - items: List of course objects
    """
    # Validate limit
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 1
    
    # Build query
    query = db.query(Course)
    
    # Apply filters
    filters = {}
    if track_type:
        query = query.filter(Course.track_type == track_type)
        filters["track_type"] = track_type
    
    if level:
        query = query.filter(Course.level == level)
        filters["level"] = level
    
    # Get total count
    total_count = query.count()
    
    # Calculate pagination
    page = (skip // limit) + 1 if skip > 0 else 1
    pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    # Get courses for this page
    courses = query.offset(skip).limit(limit).all()
    
    return {
        "skip": skip,
        "limit": limit,
        "total": total_count,
        "count": len(courses),
        "page": page,
        "pages": pages,
        "filters": filters,
        "items": courses
    }


@router.get("/filter-options", response_model=dict)
def get_course_filter_options(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get available filter options for course listing.
    
    Returns:
    - track_types: List of unique track types
    - levels: List of unique levels
    - total_courses: Total number of courses in system
    """
    # Get unique track types
    track_types = db.query(distinct(Course.track_type)).filter(
        Course.track_type.isnot(None)
    ).all()
    track_types = [t[0] for t in track_types if t[0]]
    
    # Get unique levels
    levels = db.query(distinct(Course.level)).filter(
        Course.level.isnot(None)
    ).all()
    levels = [l[0] for l in levels if l[0]]
    
    # Get total course count
    total_courses = db.query(Course).count()
    
    return {
        "track_types": sorted(track_types),
        "levels": sorted(levels),
        "total_courses": total_courses
    }


@router.get("/{course_id}", response_model=CourseDetailResponse)
def get_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific course by ID with all its modules and lessons.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    return course


@router.put("/{course_id}", response_model=CourseResponse)
def update_course(
    course_id: int,
    course_update: CourseUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update a course (admin only).
    
    Requires admin role to update courses.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    # Update fields if provided
    if course_update.title is not None:
        course.title = course_update.title
    if course_update.description is not None:
        course.description = course_update.description
    if course_update.track_type is not None:
        course.track_type = course_update.track_type
    if course_update.level is not None:
        course.level = course_update.level
    
    db.commit()
    db.refresh(course)
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete a course (admin only).
    
    Requires admin role. Cascades to delete all associated modules and lessons.
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    db.delete(course)
    db.commit()


# ==================== MODULE ENDPOINTS ====================

@router.post("/{course_id}/modules", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
def create_module(
    course_id: int,
    module: ModuleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new module for a course (admin only).
    
    Requires admin role to add modules to courses.
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    db_module = Module(
        course_id=course_id,
        title=module.title,
        order_number=module.order_number,
    )
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module


@router.get("/{course_id}/modules", response_model=list[ModuleResponse])
def get_course_modules(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all modules for a specific course.
    """
    # Verify course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found"
        )
    
    modules = db.query(Module).filter(Module.course_id == course_id).order_by(Module.order_number).all()
    return modules


@router.put("/modules/{module_id}", response_model=ModuleResponse)
def update_module(
    module_id: int,
    module_update: ModuleCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update a module (admin only).
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    module.title = module_update.title
    module.order_number = module_update.order_number
    
    db.commit()
    db.refresh(module)
    return module


@router.delete("/modules/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_module(
    module_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete a module (admin only).
    
    Cascades to delete all associated lessons.
    """
    module = db.query(Module).filter(Module.id == module_id).first()
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    db.delete(module)
    db.commit()


# ==================== LESSON ENDPOINTS ====================

@router.post("/modules/{module_id}/lessons", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    module_id: int,
    lesson: LessonCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Create a new lesson for a module (admin only).
    
    Requires admin role to add lessons to modules.
    """
    # Verify module exists
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    db_lesson = Lesson(
        module_id=module_id,
        title=lesson.title,
        content=lesson.content,
        video_url=lesson.video_url,
        duration_minutes=lesson.duration_minutes,
    )
    db.add(db_lesson)
    db.commit()
    db.refresh(db_lesson)
    return db_lesson


@router.get("/modules/{module_id}/lessons", response_model=list[LessonResponse])
def get_module_lessons(
    module_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all lessons for a specific module.
    """
    # Verify module exists
    module = db.query(Module).filter(Module.id == module_id).first()
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module with id {module_id} not found"
        )
    
    lessons = db.query(Lesson).filter(Lesson.module_id == module_id).all()
    return lessons


@router.get("/lessons/{lesson_id}", response_model=LessonResponse)
def get_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific lesson by ID.
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    return lesson


@router.put("/lessons/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_update: LessonCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Update a lesson (admin only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    if lesson_update.title is not None:
        lesson.title = lesson_update.title
    if lesson_update.content is not None:
        lesson.content = lesson_update.content
    if lesson_update.video_url is not None:
        lesson.video_url = lesson_update.video_url
    if lesson_update.duration_minutes is not None:
        lesson.duration_minutes = lesson_update.duration_minutes
    
    db.commit()
    db.refresh(lesson)
    return lesson


@router.delete("/lessons/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """
    Delete a lesson (admin only).
    """
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson with id {lesson_id} not found"
        )
    
    db.delete(lesson)
    db.commit()
