from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.prediction import StudentPredictionInput, PredictionResponse
from routes.auth import get_current_user, get_student_for_user
from services.learning_signal_service import build_learning_feature_vector
from services.ml_service import predict_track as predict_track_with_model

router = APIRouter(
    prefix="/predict",
    tags=["predictions"],
)


TRACK_ALIASES = {
    "Social_Sciences": "Social Studies",
    "Social Sciences": "Social Studies",
    "Computer_Basics": "Computer Basics",
}


def canonical_track(track: str) -> str:
    return TRACK_ALIASES.get(track, track.replace("_", " "))

@router.post("/predict-track", response_model=PredictionResponse)
def predict_track(student: StudentPredictionInput):
    """
    Predict the best career track for a student based on their scores and metrics.
    
    Input:
    - math_score: 0-100
    - verbal_score: 0-100
    - logic_score: 0-100
    - creative_score: 0-100
    - confidence_level: 0.0-1.0
    - attendance_rate: 0.0-1.0
    
    Output:
    - predicted_track: The recommended career track
    - probability: Confidence level of the prediction
    - all_probabilities: Probability for each track class
    """
    try:
        result = predict_track_with_model(
            math_score=student.math_score,
            verbal_score=student.verbal_score,
            logic_score=student.logic_score,
            creative_score=student.creative_score,
            confidence_level=student.confidence_level,
            attendance_rate=student.attendance_rate,
            quiz_success_rate=student.quiz_success_rate,
            lesson_completion_rate=student.lesson_completion_rate,
            learning_pace=student.learning_pace,
            consistency_score=student.consistency_score,
        )
        return PredictionResponse(
            predicted_track=canonical_track(result["predicted_track"]),
            probability=result["probability"],
            all_probabilities={
                canonical_track(track): probability
                for track, probability in result["all_probabilities"].items()
            }
        )
    
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model file not found. Train the model first."
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(e)}"
        )


@router.get("/my-track", response_model=dict)
def predict_my_track(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Predict a track from the authenticated student's real learning signals.
    """
    student = get_student_for_user(db, current_user)
    signals = build_learning_feature_vector(current_user, student, db)
    try:
        result = predict_track_with_model(
            math_score=signals["math_score"],
            verbal_score=signals["verbal_score"],
            logic_score=signals["logic_score"],
            creative_score=signals["creative_score"],
            confidence_level=signals["confidence_level"],
            attendance_rate=signals["attendance_rate"],
            quiz_success_rate=signals["quiz_success_rate"],
            lesson_completion_rate=signals["lesson_completion_rate"],
            learning_pace=signals["learning_pace"],
            consistency_score=signals["consistency_score"],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction error: {str(exc)}"
        )

    return {
        "predicted_track": canonical_track(result["predicted_track"]),
        "probability": result["probability"],
        "all_probabilities": {
            canonical_track(track): probability
            for track, probability in result["all_probabilities"].items()
        },
        "signals": signals,
        "model_version": result.get("model_version"),
    }
