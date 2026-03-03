from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class LessonProgress(Base):
    """LessonProgress model for database - tracks individual lesson completion by students"""
    __tablename__ = "lesson_progress"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Progress Information
    completed = Column(Boolean, default=False, nullable=False, index=True)
    completion_date = Column(DateTime, nullable=True)  # Null until lesson is completed
    
    # Timestamps
    started_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    
    # Relationships
    student = relationship(
        "Student",
        foreign_keys=[student_id],
        lazy="joined"
    )
    lesson = relationship(
        "Lesson",
        foreign_keys=[lesson_id],
        lazy="joined"
    )
    
    # Unique constraint to prevent duplicate progress entries
    __table_args__ = (
        UniqueConstraint('student_id', 'lesson_id', name='unique_student_lesson_progress'),
    )
    
    def __repr__(self):
        return f"<LessonProgress(id={self.id}, student_id={self.student_id}, lesson_id={self.lesson_id}, completed={self.completed})>"
