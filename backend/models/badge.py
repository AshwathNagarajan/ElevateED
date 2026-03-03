from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from datetime import datetime
import enum


class BadgeConditionType(str, enum.Enum):
    """Types of conditions for earning badges."""
    COMPLETE_COURSE = "complete_course"
    LEARNING_STREAK = "learning_streak"
    HIGH_SCORE = "high_score"
    QUIZ_MASTER = "quiz_master"
    ATTENDANCE_PERFECT = "attendance_perfect"
    FIRST_LESSON = "first_lesson"
    MODULE_COMPLETION = "module_completion"
    PRACTICE_DEDICATION = "practice_dedication"


class Badge(Base):
    """
    Badge model for gamification and student achievement tracking.
    
    Badges are milestones students can earn by meeting specific conditions.
    Examples include completing courses, maintaining streaks, or achieving high scores.
    """
    __tablename__ = "badges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=False)
    condition_type = Column(Enum(BadgeConditionType), nullable=False, index=True)
    
    # Badge icon/image URL
    icon_url = Column(String(500), nullable=True)
    
    # Badge color for frontend display
    color = Column(String(50), default="primary")  # "primary", "secondary", "success", "warning", etc.
    
    # Points awarded for earning this badge
    points = Column(Integer, default=10)
    
    # Whether the badge is active/visible
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    # Relationships
    earned_by_students = relationship(
        "StudentBadge",
        back_populates="badge",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Badge(id={self.id}, name={self.name}, condition={self.condition_type})>"


class StudentBadge(Base):
    """
    StudentBadge model to track which students have earned which badges.
    
    Records the moment a student earned a badge for achievement recognition
    and progress tracking.
    """
    __tablename__ = "student_badges"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("badges.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # When the badge was earned
    earned_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Context/reason for earning badge (e.g., course_id, streak_count)
    context_data = Column(String(500), nullable=True)

    # Relationships
    student = relationship(
        "Student",
        back_populates="earned_badges",
        lazy="joined"
    )
    badge = relationship(
        "Badge",
        back_populates="earned_by_students",
        lazy="joined"
    )

    # Unique constraint: each student can only earn each badge once
    __table_args__ = (
        Index('ix_student_badge_unique', 'student_id', 'badge_id', unique=True),
    )

    def __repr__(self):
        return f"<StudentBadge(id={self.id}, student_id={self.student_id}, badge_id={self.badge_id}, earned_at={self.earned_at})>"
