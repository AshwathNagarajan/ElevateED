from sqlalchemy import Column, Integer, Boolean, Date, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from database import Base


class Attendance(Base):
    """Attendance model for tracking student attendance records"""
    __tablename__ = "attendance"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    
    # Attendance Information
    date = Column(Date, nullable=False, index=True)
    present = Column(Boolean, nullable=False, default=True)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Create composite index for efficient queries by student and date
    __table_args__ = (
        Index('idx_student_date', 'student_id', 'date'),
    )
    
    def __repr__(self):
        return f"<Attendance(student_id={self.student_id}, date={self.date}, present={self.present})>"
