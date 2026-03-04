from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Enrollment(Base):
    """Enrollment model for database - tracks student enrollment in courses"""
    __tablename__ = "enrollments"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Enrollment Information
    progress_percentage = Column(Float, default=0.0, nullable=False)  # 0-100
    completed = Column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    enrolled_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    student = relationship(
        "User",
        foreign_keys=[student_id],
        lazy="joined"
    )
    course = relationship(
        "Course",
        foreign_keys=[course_id],
        lazy="joined"
    )
    
    # Unique constraint to prevent duplicate enrollments
    __table_args__ = (
        UniqueConstraint('student_id', 'course_id', name='unique_student_course_enrollment'),
    )
    
    def __repr__(self):
        return f"<Enrollment(id={self.id}, student_id={self.student_id}, course_id={self.course_id}, progress={self.progress_percentage}%, completed={self.completed})>"
