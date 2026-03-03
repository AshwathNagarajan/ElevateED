from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base


class WeeklySkillScore(Base):
    """Weekly Skill Score model for tracking student skill progression"""
    __tablename__ = "weekly_skill_scores"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign Key
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False, index=True)
    
    # Score Components
    quiz_score = Column(Float, nullable=False)
    project_score = Column(Float, nullable=False)
    attendance_score = Column(Float, nullable=False)
    mentor_rating = Column(Float, nullable=False)
    
    # Calculated Score
    skill_score = Column(Float, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    week_ending = Column(DateTime, nullable=False, index=True)
    
    def __repr__(self):
        return f"<WeeklySkillScore(student_id={self.student_id}, skill_score={self.skill_score}, week_ending={self.week_ending})>"
