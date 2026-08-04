from pydantic import BaseModel, ConfigDict
from typing import Dict

class StudentPredictionInput(BaseModel):
    """Schema for student prediction input"""
    math_score: int
    verbal_score: int
    logic_score: int
    creative_score: int
    confidence_level: float
    attendance_rate: float
    quiz_success_rate: float = 0.5
    lesson_completion_rate: float = 0.5
    learning_pace: float = 0.5
    consistency_score: float = 0.5

class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    predicted_track: str
    probability: float
    all_probabilities: Dict[str, float]
    
    model_config = ConfigDict(validate_assignment=True)
