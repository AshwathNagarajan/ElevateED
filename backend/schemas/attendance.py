from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional


class AttendanceCreate(BaseModel):
    """Schema for creating an attendance record"""
    student_id: int
    attendance_date: date = Field(..., description="Attendance date")
    present: bool = Field(default=True, description="Whether student was present")


class AttendanceUpdate(BaseModel):
    """Schema for updating an attendance record"""
    attendance_date: Optional[date] = None
    present: Optional[bool] = None


class AttendanceResponse(BaseModel):
    """Schema for attendance record response"""
    id: int
    student_id: int
    attendance_date: date = Field(..., alias="date")
    present: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class AttendanceStatistics(BaseModel):
    """Schema for attendance statistics"""
    student_id: int
    total_days: int
    present_days: int
    absent_days: int
    attendance_percentage: float = Field(..., description="Attendance percentage (0-100)")
    
    model_config = ConfigDict(from_attributes=True)
