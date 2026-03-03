from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
from database import get_db
from models.attendance import Attendance
from schemas.attendance import (
    AttendanceCreate,
    AttendanceUpdate,
    AttendanceResponse,
    AttendanceStatistics
)

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
)


@router.post("/", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance(
    attendance: AttendanceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new attendance record for a student.
    
    Args:
        attendance: AttendanceCreate schema with student_id, attendance_date, and present status
        db: Database session
    
    Returns:
        AttendanceResponse: Created attendance record
    """
    db_attendance = Attendance(
        student_id=attendance.student_id,
        date=attendance.attendance_date,
        present=attendance.present
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@router.post("/mark", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def mark_attendance(
    student_id: int,
    attendance_date: date = None,
    present: bool = True,
    db: Session = Depends(get_db)
):
    """
    Quick endpoint to mark attendance for a student.
    
    Args:
        student_id: The student ID
        attendance_date: Date to mark attendance (defaults to today)
        present: Whether the student was present (defaults to True)
        db: Database session
    
    Returns:
        AttendanceResponse: Created attendance record
    """
    if attendance_date is None:
        attendance_date = date.today()
    
    # Check if attendance record already exists for this student on this date
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == attendance_date
    ).first()
    
    if existing:
        # Update existing record
        existing.present = present
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new record
    db_attendance = Attendance(
        student_id=student_id,
        date=attendance_date,
        present=present
    )
    db.add(db_attendance)
    db.commit()
    db.refresh(db_attendance)
    return db_attendance


@router.get("/percentage/{student_id}")
def get_attendance_percentage(
    student_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get attendance percentage for a student over a specified number of days.
    
    Args:
        student_id: The student ID
        days: Number of past days to include (default: 30)
        db: Database session
    
    Returns:
        dict: Contains attendance_percentage and related statistics
    
    Raises:
        HTTPException: If no attendance records found
    """
    start_date = date.today() - timedelta(days=days)
    
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date >= start_date
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for student {student_id} in the last {days} days"
        )
    
    total_days = len(records)
    present_days = sum(1 for r in records if r.present)
    absent_days = total_days - present_days
    attendance_percentage = round((present_days / total_days) * 100, 2) if total_days > 0 else 0
    
    return {
        "student_id": student_id,
        "attendance_percentage": attendance_percentage,
        "present_days": present_days,
        "absent_days": absent_days,
        "total_days": total_days,
        "period_days": days
    }


@router.get("/{student_id}", response_model=list[AttendanceResponse])
def get_student_attendance_records(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all attendance records for a specific student.
    
    Args:
        student_id: The student ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        list[AttendanceResponse]: List of attendance records
    """
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for student {student_id}"
        )
    
    return records


@router.get("/student/{student_id}", response_model=list[AttendanceResponse])
def get_student_attendance(
    student_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get all attendance records for a specific student (alias endpoint).
    
    Args:
        student_id: The student ID
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        list[AttendanceResponse]: List of attendance records
    """
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id
    ).order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    
    return records


@router.get("/student/{student_id}/statistics", response_model=AttendanceStatistics)
def get_attendance_statistics(
    student_id: int,
    days: int = 30,
    db: Session = Depends(get_db)
):
    """
    Get attendance statistics for a student over a specified number of days.
    
    Args:
        student_id: The student ID
        days: Number of past days to include in statistics (default: 30)
        db: Database session
    
    Returns:
        AttendanceStatistics: Attendance statistics including percentage
    
    Raises:
        HTTPException: If no attendance records found
    """
    start_date = date.today() - timedelta(days=days)
    
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date >= start_date
    ).all()
    
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No attendance records found for student {student_id} in the last {days} days"
        )
    
    total_days = len(records)
    present_days = sum(1 for r in records if r.present)
    absent_days = total_days - present_days
    attendance_percentage = round((present_days / total_days) * 100, 2) if total_days > 0 else 0
    
    return AttendanceStatistics(
        student_id=student_id,
        total_days=total_days,
        present_days=present_days,
        absent_days=absent_days,
        attendance_percentage=attendance_percentage
    )


@router.get("/record/{attendance_id}", response_model=AttendanceResponse)
def get_attendance_by_id(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific attendance record by ID.
    
    Args:
        attendance_id: The attendance record ID
        db: Database session
    
    Returns:
        AttendanceResponse: The attendance record
    
    Raises:
        HTTPException: If record not found
    """
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with id {attendance_id} not found"
        )
    
    return record


@router.put("/record/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(
    attendance_id: int,
    update_data: AttendanceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an attendance record.
    
    Args:
        attendance_id: The attendance record ID
        update_data: Updated attendance data (attendance_date and/or present status)
        db: Database session
    
    Returns:
        AttendanceResponse: Updated attendance record
    
    Raises:
        HTTPException: If record not found
    """
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with id {attendance_id} not found"
        )
    
    if update_data.attendance_date is not None:
        record.date = update_data.attendance_date
    if update_data.present is not None:
        record.present = update_data.present
    
    db.commit()
    db.refresh(record)
    
    return record


@router.delete("/record/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance(
    attendance_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an attendance record.
    
    Args:
        attendance_id: The attendance record ID
        db: Database session
    
    Raises:
        HTTPException: If record not found
    """
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record with id {attendance_id} not found"
        )
    
    db.delete(record)
    db.commit()
