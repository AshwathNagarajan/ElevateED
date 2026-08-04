"""
ML Service for model loading, caching, and predictions.

⚠️  SECURITY WARNING ⚠️
This service ONLY loads models from trusted local paths defined below.
NEVER load model files from user-uploaded sources, network URLs, or untrusted locations.
Model files should be pre-trained and version-controlled in the repository.

Supported model format: pickle (.pkl) files containing dict with 'model' and 'label_encoder' keys
Model format must match the structure created by ml/train_model.py
"""

import pickle
import os
from typing import Dict, Optional, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# MODEL METADATA & CONSTANTS
# ============================================================================

# Model version - increment when retraining
MODEL_VERSION = "2.0"
MODEL_CREATED_DATE = "2026-08-04"

# Supported career tracks (must match label encoder classes from training)
SUPPORTED_TRACKS = [
    "Business Analytics",
    "Commerce",
    "Computer Science",
    "Data Science",
    "Design",
    "Engineering",
    "Humanities",
    "Life Science",
]

# Feature names and expected ranges for validation
FEATURE_SPECS = {
    "math_score": {"min": 0, "max": 100, "type": "int"},
    "verbal_score": {"min": 0, "max": 100, "type": "int"},
    "logic_score": {"min": 0, "max": 100, "type": "int"},
    "creative_score": {"min": 0, "max": 100, "type": "int"},
    "confidence_level": {"min": 0.0, "max": 1.0, "type": "float"},
    "attendance_rate": {"min": 0.0, "max": 1.0, "type": "float"},
    "quiz_success_rate": {"min": 0.0, "max": 1.0, "type": "float"},
    "lesson_completion_rate": {"min": 0.0, "max": 1.0, "type": "float"},
    "learning_pace": {"min": 0.0, "max": 1.0, "type": "float"},
    "consistency_score": {"min": 0.0, "max": 1.0, "type": "float"},
}

# ============================================================================
# MODEL LOADING & CACHING
# ============================================================================

# Global model cache - loaded once at startup or lazily on first use
_CACHED_MODEL = None
_CACHED_LABEL_ENCODER = None
_MODEL_LOAD_ERROR = None

# ONLY local trusted path allowed for model loading
TRUSTED_MODEL_PATHS = [
    os.path.join(os.path.dirname(__file__), '..', 'ml', 'model.pkl'),
]


def get_trusted_model_path() -> str:
    """Get the single trusted model path"""
    return TRUSTED_MODEL_PATHS[0]


def _validate_model_path(model_path: str) -> None:
    """
    Validate that model path is in the trusted locations.
    
    ⚠️  SECURITY: This prevents loading models from:
    - User-uploaded files
    - Network URLs
    - Arbitrary filesystem locations
    - Untrusted sources
    
    Args:
        model_path: Path to model file
        
    Raises:
        ValueError: If path is not in trusted locations
    """
    abs_path = os.path.abspath(model_path)
    
    for trusted_path in TRUSTED_MODEL_PATHS:
        trusted_abs = os.path.abspath(trusted_path)
        if abs_path == trusted_abs:
            return
    
    logger.error(f"❌ SECURITY: Attempted to load model from untrusted path: {model_path}")
    raise ValueError(
        f"Model path not in trusted locations. Only local pre-trained models are supported. "
        f"Attempted path: {model_path}"
    )


def load_model_from_disk(model_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load model and label encoder from pickle file.
    
    This function:
    1. Validates model path is trusted (security)
    2. Checks file exists and is readable
    3. Validates pickle structure
    4. Returns model and label encoder
    
    ⚠️  IMPORTANT: This is for trusted, pre-trained models only.
    Do NOT call this with user-supplied paths.
    
    Args:
        model_path: Optional path to model. Uses default if not provided.
        
    Returns:
        Dict with 'model' and 'label_encoder' keys
        
    Raises:
        FileNotFoundError: If model file doesn't exist
        ValueError: If model path is not trusted or structure is invalid
        RuntimeError: If file is corrupt or cannot be loaded
    """
    if model_path is None:
        model_path = get_trusted_model_path()
    
    # SECURITY: Validate path is trusted
    _validate_model_path(model_path)
    
    # Check file exists
    if not os.path.exists(model_path):
        logger.error(f"Model file not found: {model_path}")
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            f"Train the model first using: python ml/train_model.py"
        )
    
    # Check file is readable
    if not os.access(model_path, os.R_OK):
        logger.error(f"Model file is not readable: {model_path}")
        raise PermissionError(
            f"Model file is not readable: {model_path}. "
            f"Check file permissions."
        )
    
    # Check file size (sanity check - models should be > 100KB, < 100MB)
    file_size = os.path.getsize(model_path)
    if file_size < 100_000:
        logger.error(f"Model file is suspiciously small ({file_size} bytes): {model_path}")
        raise RuntimeError(
            f"Model file appears to be corrupt (too small: {file_size} bytes). "
            f"Retrain the model."
        )
    if file_size > 100_000_000:
        logger.error(f"Model file is suspiciously large ({file_size} bytes): {model_path}")
        raise RuntimeError(
            f"Model file appears to be corrupt (too large: {file_size} bytes). "
            f"Retrain the model."
        )
    
    try:
        logger.debug(f"Loading model from {model_path} (size: {file_size} bytes)")
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
    except (pickle.UnpicklingError, EOFError) as e:
        logger.error(f"Failed to unpickle model file: {str(e)}")
        raise RuntimeError(
            f"Model file is corrupt (failed to load pickle): {str(e)}. "
            f"Retrain the model using: python ml/train_model.py"
        )
    except Exception as e:
        logger.error(f"Unexpected error loading model: {type(e).__name__}: {str(e)}")
        raise RuntimeError(
            f"Failed to load model file: {type(e).__name__}. "
            f"Try retraining the model."
        )
    
    # Validate model structure
    if not isinstance(model_data, dict):
        logger.error(f"Model data is not a dict: {type(model_data)}")
        raise ValueError(
            f"Invalid model format. Expected dict, got {type(model_data)}. "
            f"Model must be saved as dict with 'model' and 'label_encoder' keys."
        )
    
    required_keys = {'model', 'label_encoder'}
    if not required_keys.issubset(model_data.keys()):
        missing = required_keys - model_data.keys()
        logger.error(f"Model dict missing required keys: {missing}")
        raise ValueError(
            f"Invalid model structure. Missing keys: {missing}. "
            f"Model dict must contain 'model' and 'label_encoder' keys."
        )
    
    model = model_data['model']
    label_encoder = model_data['label_encoder']
    
    # Validate label encoder has expected classes
    try:
        classes = list(label_encoder.classes_)
        logger.info(f"Model loaded successfully. Classes: {classes}")
        if classes != SUPPORTED_TRACKS:
            logger.warning(
                f"Model classes don't match expected tracks. "
                f"Expected: {SUPPORTED_TRACKS}, Got: {classes}"
            )
    except Exception as e:
        logger.error(f"Cannot access label encoder classes: {str(e)}")
        raise ValueError(
            f"Model label encoder is invalid: {str(e)}"
        )
    
    return model_data


def get_cached_model() -> Dict[str, Any]:
    """
    Get cached model or load it if not cached.
    
    Lazy loads model on first use. Subsequent calls return cached version.
    If model fails to load, raises exception with helpful error message.
    
    Returns:
        Dict with 'model' and 'label_encoder' keys
        
    Raises:
        RuntimeError: If model cannot be loaded (with detailed error)
    """
    global _CACHED_MODEL, _CACHED_LABEL_ENCODER, _MODEL_LOAD_ERROR
    
    # If already cached, return it
    if _CACHED_MODEL is not None:
        return {
            'model': _CACHED_MODEL,
            'label_encoder': _CACHED_LABEL_ENCODER
        }
    
    # If error cached, raise it again
    if _MODEL_LOAD_ERROR is not None:
        raise RuntimeError(_MODEL_LOAD_ERROR)
    
    # Try to load model
    try:
        model_data = load_model_from_disk()
        _CACHED_MODEL = model_data['model']
        _CACHED_LABEL_ENCODER = model_data['label_encoder']
        logger.info("✅ Model cached successfully for subsequent requests")
        return model_data
    except Exception as e:
        error_msg = str(e)
        _MODEL_LOAD_ERROR = error_msg
        logger.error(f"❌ Model loading failed (will not retry): {error_msg}")
        raise RuntimeError(error_msg)


# ============================================================================
# PREDICTION INPUT VALIDATION
# ============================================================================

def validate_prediction_input(
    math_score: int,
    verbal_score: int,
    logic_score: int,
    creative_score: int,
    confidence_level: float,
    attendance_rate: float,
    quiz_success_rate: float = 0.5,
    lesson_completion_rate: float = 0.5,
    learning_pace: float = 0.5,
    consistency_score: float = 0.5,
) -> None:
    """
    Strictly validate all prediction input parameters.
    
    Checks:
    - All values are within expected ranges
    - Values are of correct types (or convertible)
    - No NaN, Inf, or other invalid values
    
    Args:
        math_score, verbal_score, logic_score, creative_score: 0-100 scores
        confidence_level, attendance_rate: 0.0-1.0 rates
        
    Raises:
        ValueError: If any input is invalid
    """
    inputs = {
        "math_score": math_score,
        "verbal_score": verbal_score,
        "logic_score": logic_score,
        "creative_score": creative_score,
        "confidence_level": confidence_level,
        "attendance_rate": attendance_rate,
        "quiz_success_rate": quiz_success_rate,
        "lesson_completion_rate": lesson_completion_rate,
        "learning_pace": learning_pace,
        "consistency_score": consistency_score,
    }
    
    for field_name, value in inputs.items():
        spec = FEATURE_SPECS[field_name]
        
        # Check type
        expected_type = spec["type"]
        if expected_type == "int" and not isinstance(value, int):
            raise ValueError(
                f"Invalid {field_name}: expected int, got {type(value).__name__} "
                f"(value={value})"
            )
        if expected_type == "float" and not isinstance(value, (float, int)):
            raise ValueError(
                f"Invalid {field_name}: expected float, got {type(value).__name__} "
                f"(value={value})"
            )
        
        # Check for NaN and Inf
        try:
            if isinstance(value, float):
                if value != value:  # NaN check
                    raise ValueError(f"{field_name} is NaN")
                if value == float('inf') or value == float('-inf'):
                    raise ValueError(f"{field_name} is infinity")
        except (TypeError, ValueError):
            pass
        
        # Check range
        min_val = spec["min"]
        max_val = spec["max"]
        if not (min_val <= value <= max_val):
            raise ValueError(
                f"Invalid {field_name}: expected {min_val}-{max_val}, got {value}"
            )
    
    logger.debug(
        f"✓ Prediction inputs validated: "
        f"scores=[{math_score},{verbal_score},{logic_score},{creative_score}], "
        f"rates=[{confidence_level},{attendance_rate}]"
    )


def preprocess_features(
    math_score: int,
    verbal_score: int,
    logic_score: int,
    creative_score: int,
    confidence_level: float,
    attendance_rate: float,
    quiz_success_rate: float = 0.5,
    lesson_completion_rate: float = 0.5,
    learning_pace: float = 0.5,
    consistency_score: float = 0.5,
) -> list:
    """
    Preprocess student features for model prediction.
    
    Normalizes scores from 0-100 range to 0.0-1.0 for ML model.
    Returns as 2D array for sklearn compatibility.
    
    Args:
        Validated input parameters (must be validated before calling this)
        
    Returns:
        2D list suitable for model.predict()
    """
    features = [
        math_score / 100.0,
        verbal_score / 100.0,
        logic_score / 100.0,
        creative_score / 100.0,
        confidence_level,
        attendance_rate,
        quiz_success_rate,
        lesson_completion_rate,
        learning_pace,
        consistency_score,
    ]
    return [features]  # 2D array for sklearn


# ============================================================================
# PREDICTION
# ============================================================================

def predict_track(
    math_score: int,
    verbal_score: int,
    logic_score: int,
    creative_score: int,
    confidence_level: float,
    attendance_rate: float,
    quiz_success_rate: float = 0.5,
    lesson_completion_rate: float = 0.5,
    learning_pace: float = 0.5,
    consistency_score: float = 0.5,
) -> Dict[str, Any]:
    """
    Predict career track for a student.
    
    Args:
        All validated student metrics
        
    Returns:
        Dict with:
        - predicted_track: str (recommended track)
        - probability: float (confidence 0.0-1.0)
        - all_probabilities: dict (track -> probability)
        - model_version: str (for debugging)
        
    Raises:
        ValueError: If inputs invalid
        RuntimeError: If model cannot be loaded
    """
    # Validate inputs
    validate_prediction_input(
        math_score, verbal_score, logic_score, creative_score,
        confidence_level, attendance_rate, quiz_success_rate,
        lesson_completion_rate, learning_pace, consistency_score
    )
    
    # Get cached model
    model_data = get_cached_model()
    model = model_data['model']
    label_encoder = model_data['label_encoder']
    
    # Preprocess features
    features = preprocess_features(
        math_score, verbal_score, logic_score, creative_score,
        confidence_level, attendance_rate, quiz_success_rate,
        lesson_completion_rate, learning_pace, consistency_score
    )
    
    # Make prediction
    try:
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
    except Exception as e:
        logger.error(f"Model prediction failed: {type(e).__name__}: {str(e)}")
        raise RuntimeError(
            f"Prediction failed: {type(e).__name__}. "
            f"This may indicate a model corruption. Try retraining."
        )
    
    # Get predicted track name
    try:
        predicted_track = label_encoder.inverse_transform([prediction])[0]
    except Exception as e:
        logger.error(f"Failed to decode prediction: {str(e)}")
        raise RuntimeError(f"Failed to decode model output: {str(e)}")
    
    # Get confidence (probability of predicted class)
    confidence = float(probabilities[prediction])
    
    # Create probability dictionary for all classes
    all_probabilities = {
        track: float(prob)
        for track, prob in zip(label_encoder.classes_, probabilities)
    }
    
    return {
        "predicted_track": predicted_track,
        "probability": confidence,
        "all_probabilities": all_probabilities,
        "model_version": MODEL_VERSION,
    }


def get_model_metadata() -> Dict[str, Any]:
    """
    Get model metadata for debugging and info endpoints.
    
    Returns:
        Dict with model version, creation date, supported tracks, etc.
    """
    return {
        "model_version": MODEL_VERSION,
        "model_created": MODEL_CREATED_DATE,
        "supported_tracks": SUPPORTED_TRACKS,
        "feature_count": len(FEATURE_SPECS),
        "feature_names": list(FEATURE_SPECS.keys()),
    }
