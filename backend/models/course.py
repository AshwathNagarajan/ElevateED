from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Course(Base):
    """Course model for database"""
    __tablename__ = "courses"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Course Information
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    track_type = Column(String(100), nullable=False, index=True)
    level = Column(String(50), nullable=False)  # e.g., "Beginner", "Intermediate", "Advanced"
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    modules = relationship(
        "Module",
        back_populates="course",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title}, track_type={self.track_type}, level={self.level})>"


class Module(Base):
    """Module model for database"""
    __tablename__ = "modules"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    course_id = Column(Integer, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Module Information
    title = Column(String(255), nullable=False, index=True)
    order_number = Column(Integer, nullable=False)  # Order within the course
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship(
        "Lesson",
        back_populates="module",
        cascade="all, delete-orphan",
        lazy="joined"
    )
    
    def __repr__(self):
        return f"<Module(id={self.id}, course_id={self.course_id}, title={self.title}, order={self.order_number})>"


class Lesson(Base):
    """Lesson model for database"""
    __tablename__ = "lessons"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Lesson Information
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    duration_minutes = Column(Integer, nullable=True)  # Duration in minutes
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="lessons")
    quizzes = relationship(
        "Quiz",
        back_populates="lesson",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Lesson(id={self.id}, module_id={self.module_id}, title={self.title}, duration={self.duration_minutes}min)>"
