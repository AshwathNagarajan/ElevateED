from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Student(Base):
    """Student model for database"""
    __tablename__ = "students"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to User (authentication)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=True, index=True)
    
    # Personal Information
    name = Column(String(255), nullable=False, index=True)
    age = Column(Integer, nullable=True, default=0)
    guardian_contact = Column(String(255), nullable=True, default="")
    
    # Track Information
    interest_track = Column(String(100), nullable=True)
    predicted_track = Column(String(100), nullable=True)
    
    # Timestamps (using func.now() for database-side default)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="joined"
    )
    quiz_submissions = relationship(
        "QuizSubmission",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="select"
    )
    earned_badges = relationship(
        "StudentBadge",
        back_populates="student",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<Student(id={self.id}, name={self.name}, user_id={self.user_id})>"
