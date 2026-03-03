from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class AnswerChoice(str, Enum):
    """Valid answer choices."""
    A = "a"
    B = "b"
    C = "c"
    D = "d"


class QuizCreate(BaseModel):
    """Schema for creating a quiz."""
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: AnswerChoice


class QuizResponse(BaseModel):
    """Schema for quiz response with all details."""
    id: int
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    created_at: datetime

    class Config:
        from_attributes = True


class QuizWithoutAnswer(BaseModel):
    """Schema for quiz response without revealing the correct answer."""
    id: int
    lesson_id: int
    question: str
    option_a: str
    option_b: str
    option_c: str
    option_d: str

    class Config:
        from_attributes = True


class QuizSubmissionRequest(BaseModel):
    """Schema for submitting a quiz answer."""
    selected_answer: AnswerChoice = Field(
        ...,
        description="Student's selected answer (a, b, c, or d)"
    )


class QuizSubmissionResponse(BaseModel):
    """Schema for quiz submission response with score."""
    id: int
    student_id: int
    quiz_id: int
    selected_answer: AnswerChoice
    score: int
    is_correct: bool
    submitted_at: datetime
    question: Optional[str] = None
    correct_answer: Optional[AnswerChoice] = None

    class Config:
        from_attributes = True


class QuizSubmissionDetail(BaseModel):
    """Detailed quiz submission with quiz info."""
    id: int
    student_id: int
    quiz_id: int
    selected_answer: AnswerChoice
    score: int
    is_correct: bool
    submitted_at: datetime

    class Config:
        from_attributes = True
