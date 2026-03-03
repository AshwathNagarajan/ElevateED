from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Enum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum


class AnswerChoice(str, enum.Enum):
    """Valid answer choices for quiz questions."""
    A = "a"
    B = "b"
    C = "c"
    D = "d"


class Quiz(Base):
    """
    Quiz model for lesson assessments.
    
    Each quiz is tied to a lesson and contains a single question
    with four multiple-choice options.
    """
    __tablename__ = "quizzes"

    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, index=True)
    question = Column(String(500), nullable=False)
    option_a = Column(String(255), nullable=False)
    option_b = Column(String(255), nullable=False)
    option_c = Column(String(255), nullable=False)
    option_d = Column(String(255), nullable=False)
    correct_answer = Column(Enum(AnswerChoice), nullable=False)  # Store as 'a', 'b', 'c', or 'd'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    lesson = relationship(
        "Lesson",
        back_populates="quizzes",
        lazy="joined"
    )
    submissions = relationship(
        "QuizSubmission",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="select"
    )

    def __repr__(self):
        return f"<Quiz(id={self.id}, lesson_id={self.lesson_id}, question='{self.question[:50]}...')>"


class QuizSubmission(Base):
    """
    Quiz submission model to track student quiz responses.
    
    Records when a student answers a quiz question and their score.
    """
    __tablename__ = "quiz_submissions"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_answer = Column(Enum(AnswerChoice), nullable=False)  # Student's answer choice
    score = Column(Integer, default=0)  # 0 for incorrect, 100 for correct (or partial score if needed)
    is_correct = Column(Boolean, default=False)  # Convenience field for quick filtering
    submitted_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    student = relationship(
        "Student",
        back_populates="quiz_submissions",
        lazy="joined"
    )
    quiz = relationship(
        "Quiz",
        back_populates="submissions",
        lazy="joined"
    )

    def __repr__(self):
        return f"<QuizSubmission(id={self.id}, student_id={self.student_id}, quiz_id={self.quiz_id}, is_correct={self.is_correct})>"
