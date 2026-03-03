import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
import os

# Model file path
MODEL_PATH = 'dropout_model.pkl'
SCALER_PATH = 'dropout_scaler.pkl'


def generate_synthetic_training_data(n_samples=500):
    """
    Generate synthetic training data for dropout risk prediction.
    
    Features:
    - attendance_rate: 0-100 (percentage)
    - skill_growth_rate: -50 to 50 (percentage change)
    - engagement_score: 0-100 (score)
    
    Target:
    - dropout_risk: 0 (no risk) or 1 (at risk)
    
    Args:
        n_samples (int): Number of training samples
    
    Returns:
        tuple: (X, y) - features and labels
    """
    np.random.seed(42)
    
    # Generate features
    attendance_rate = np.random.uniform(30, 100, n_samples)
    skill_growth_rate = np.random.uniform(-50, 50, n_samples)
    engagement_score = np.random.uniform(10, 100, n_samples)
    
    # Create target variable based on risk factors
    # Higher risk if: low attendance, negative skill growth, low engagement
    risk_probability = (
        (100 - attendance_rate) / 100 * 0.4 +  # Low attendance = higher risk
        (np.maximum(-skill_growth_rate, 0)) / 50 * 0.3 +  # Negative growth = higher risk
        (100 - engagement_score) / 100 * 0.3  # Low engagement = higher risk
    )
    
    # Add some noise and convert to binary
    dropout_risk = (risk_probability + np.random.normal(0, 0.1, n_samples) > 0.4).astype(int)
    
    # Combine features
    X = np.column_stack([attendance_rate, skill_growth_rate, engagement_score])
    
    return X, dropout_risk


def train_dropout_model(X=None, y=None, save_model=True):
    """
    Train a binary classification model to predict dropout risk.
    
    Args:
        X (array-like, optional): Training features. If None, generates synthetic data.
        y (array-like, optional): Training labels. If None, generates synthetic data.
        save_model (bool): Whether to save the trained model to disk
    
    Returns:
        tuple: (model, scaler) - trained classifier and fitted scaler
    """
    # Generate synthetic data if not provided
    if X is None or y is None:
        print("Generating synthetic training data...")
        X, y = generate_synthetic_training_data(n_samples=500)
    
    print(f"Training data shape: {X.shape}")
    print(f"Class distribution: {np.bincount(y)}")
    
    # Feature scaling
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train Random Forest model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )
    
    print("\nTraining Random Forest model...")
    model.fit(X_train, y_train)
    
    # Evaluate model
    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    print(f"\nModel Performance:")
    print(f"Training Accuracy: {train_score:.4f}")
    print(f"Testing Accuracy: {test_score:.4f}")
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_pred_proba):.4f}")
    print(f"\nClassification Report:\n{classification_report(y_test, y_pred)}")
    print(f"\nConfusion Matrix:\n{confusion_matrix(y_test, y_pred)}")
    
    # Feature importance
    feature_names = ['attendance_rate', 'skill_growth_rate', 'engagement_score']
    importance = model.feature_importances_
    print(f"\nFeature Importance:")
    for name, imp in zip(feature_names, importance):
        print(f"  {name}: {imp:.4f}")
    
    # Save model and scaler
    if save_model:
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(model, f)
        with open(SCALER_PATH, 'wb') as f:
            pickle.dump(scaler, f)
        print(f"\nModel saved to {MODEL_PATH}")
        print(f"Scaler saved to {SCALER_PATH}")
    
    return model, scaler


def load_dropout_model():
    """
    Load the trained dropout prediction model and scaler.
    
    Returns:
        tuple: (model, scaler) - loaded classifier and scaler
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Model file not found at {MODEL_PATH}")
    if not os.path.exists(SCALER_PATH):
        raise FileNotFoundError(f"Scaler file not found at {SCALER_PATH}")
    
    with open(MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
    with open(SCALER_PATH, 'rb') as f:
        scaler = pickle.load(f)
    
    return model, scaler


def predict_dropout_risk(attendance_rate, skill_growth_rate, engagement_score):
    """
    Predict dropout risk for a student.
    
    Args:
        attendance_rate (float): Student's attendance rate (0-100)
        skill_growth_rate (float): Student's skill growth rate (-50 to 50)
        engagement_score (float): Student's engagement score (0-100)
    
    Returns:
        dict: Contains 'risk_probability' and 'risk_level'
    """
    try:
        model, scaler = load_dropout_model()
    except FileNotFoundError:
        raise ValueError("Model not trained. Run train_dropout_model() first.")
    
    # Prepare features
    features = np.array([[attendance_rate, skill_growth_rate, engagement_score]])
    features_scaled = scaler.transform(features)
    
    # Get prediction probability
    risk_probability = model.predict_proba(features_scaled)[0, 1]
    
    # Determine risk level
    if risk_probability >= 0.7:
        risk_level = 'High'
    elif risk_probability >= 0.4:
        risk_level = 'Medium'
    else:
        risk_level = 'Low'
    
    return {
        'risk_probability': float(risk_probability),
        'risk_level': risk_level,
        'attendance_rate': attendance_rate,
        'skill_growth_rate': skill_growth_rate,
        'engagement_score': engagement_score
    }


def predict_dropout_risk_batch(students_data):
    """
    Predict dropout risk for multiple students.
    
    Args:
        students_data (list): List of dicts with keys:
                             - attendance_rate
                             - skill_growth_rate
                             - engagement_score
    
    Returns:
        list: List of prediction results
    """
    try:
        model, scaler = load_dropout_model()
    except FileNotFoundError:
        raise ValueError("Model not trained. Run train_dropout_model() first.")
    
    # Prepare batch features
    features = np.array([
        [
            student['attendance_rate'],
            student['skill_growth_rate'],
            student['engagement_score']
        ]
        for student in students_data
    ])
    features_scaled = scaler.transform(features)
    
    # Get predictions
    risk_probabilities = model.predict_proba(features_scaled)[:, 1]
    
    results = []
    for i, student in enumerate(students_data):
        risk_prob = risk_probabilities[i]
        if risk_prob >= 0.7:
            risk_level = 'High'
        elif risk_prob >= 0.4:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'
        
        results.append({
            'student_id': student.get('student_id', i),
            'risk_probability': float(risk_prob),
            'risk_level': risk_level,
            'attendance_rate': student['attendance_rate'],
            'skill_growth_rate': student['skill_growth_rate'],
            'engagement_score': student['engagement_score']
        })
    
    return results


if __name__ == '__main__':
    # Train the model
    model, scaler = train_dropout_model()
    
    # Test predictions
    print("\n" + "="*50)
    print("Testing Predictions")
    print("="*50)
    
    # Low risk student
    result1 = predict_dropout_risk(
        attendance_rate=95,
        skill_growth_rate=30,
        engagement_score=85
    )
    print(f"\nLow Risk Student:\n{result1}")
    
    # Medium risk student
    result2 = predict_dropout_risk(
        attendance_rate=65,
        skill_growth_rate=10,
        engagement_score=50
    )
    print(f"\nMedium Risk Student:\n{result2}")
    
    # High risk student
    result3 = predict_dropout_risk(
        attendance_rate=40,
        skill_growth_rate=-20,
        engagement_score=30
    )
    print(f"\nHigh Risk Student:\n{result3}")
    
    # Batch prediction
    batch_students = [
        {'student_id': 1, 'attendance_rate': 90, 'skill_growth_rate': 25, 'engagement_score': 80},
        {'student_id': 2, 'attendance_rate': 60, 'skill_growth_rate': 5, 'engagement_score': 45},
        {'student_id': 3, 'attendance_rate': 35, 'skill_growth_rate': -15, 'engagement_score': 25},
    ]
    
    print("\n" + "="*50)
    print("Batch Prediction Results")
    print("="*50)
    batch_results = predict_dropout_risk_batch(batch_students)
    for result in batch_results:
        print(f"\nStudent {result['student_id']}: {result}")
