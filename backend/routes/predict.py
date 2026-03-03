import pickle
import os
from fastapi import APIRouter, HTTPException, status
from schemas.prediction import StudentPredictionInput, PredictionResponse

router = APIRouter(
    prefix="/predict",
    tags=["predictions"],
)

# Load model and label encoder
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl')

def load_model():
    """Load trained model from pickle file"""
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model file not found. Train the model first."
        )
    
    with open(MODEL_PATH, 'rb') as f:
        model_data = pickle.load(f)
    
    return model_data

def preprocess_features(student_data: StudentPredictionInput) -> list:
    """Preprocess student features for prediction"""
    features = [
        student_data.math_score / 100.0,
        student_data.verbal_score / 100.0,
        student_data.logic_score / 100.0,
        student_data.creative_score / 100.0,
        student_data.confidence_level,
        student_data.attendance_rate
    ]
    return [features]  # Return as 2D array for sklearn

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
        # Load model and label encoder
        model_data = load_model()
        model = model_data['model']
        label_encoder = model_data['label_encoder']
        
        # Preprocess features
        features = preprocess_features(student)
        
        # Make prediction
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        
        # Get predicted track name
        predicted_track = label_encoder.inverse_transform([prediction])[0]
        
        # Get confidence (probability of predicted class)
        confidence = float(probabilities[prediction])
        
        # Create probability dictionary for all classes
        all_probabilities = {
            track: float(prob)
            for track, prob in zip(label_encoder.classes_, probabilities)
        }
        
        return PredictionResponse(
            predicted_track=predicted_track,
            probability=confidence,
            all_probabilities=all_probabilities
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
