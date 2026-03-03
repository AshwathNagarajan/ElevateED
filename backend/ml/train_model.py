import csv
import pickle
import random
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

# Load dataset
def load_dataset(filepath):
    """Load CSV dataset"""
    X = []
    y = []
    
    with open(filepath, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            features = [
                int(row['math_score']),
                int(row['verbal_score']),
                int(row['logic_score']),
                int(row['creative_score']),
                float(row['confidence_level']),
                float(row['attendance_rate'])
            ]
            X.append(features)
            y.append(row['target_track'])
    
    return X, y

# Preprocess features
def preprocess_features(X, y):
    """Normalize features and encode target labels"""
    # Normalize numerical features (0-100 range for scores, 0-1 for rates)
    X_normalized = []
    for sample in X:
        normalized = [
            sample[0] / 100.0,  # math_score
            sample[1] / 100.0,  # verbal_score
            sample[2] / 100.0,  # logic_score
            sample[3] / 100.0,  # creative_score
            sample[4],          # confidence_level (already 0-1)
            sample[5]           # attendance_rate (already 0-1)
        ]
        X_normalized.append(normalized)
    
    # Encode target labels
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    return X_normalized, y_encoded, le

# Split dataset
print("=" * 60)
print("ML PIPELINE: Track Prediction Model Training")
print("=" * 60)

print("\n[1] Loading dataset...")
X, y = load_dataset("student_dataset.csv")
print(f"✓ Loaded {len(X)} samples")

print("\n[2] Preprocessing features...")
X_processed, y_encoded, label_encoder = preprocess_features(X, y)
print(f"✓ Features normalized")
print(f"✓ Target classes: {list(label_encoder.classes_)}")

print("\n[3] Splitting data (80/20 train/test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X_processed, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)
print(f"✓ Training samples: {len(X_train)}")
print(f"✓ Testing samples: {len(X_test)}")

print("\n[4] Training RandomForestClassifier...")
rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=10,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)
rf_model.fit(X_train, y_train)
print(f"✓ Model trained successfully!")

print("\n[5] Evaluating model...")
y_pred = rf_model.predict(X_test)

accuracy = accuracy_score(y_test, y_pred)
f1 = f1_score(y_test, y_pred, average='weighted')

print(f"\n{'Metrics':^40}")
print("-" * 40)
print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
print(f"  F1 Score:  {f1:.4f}")
print("-" * 40)

print("\n[6] Detailed Classification Report:")
print(classification_report(
    y_test, y_pred,
    target_names=label_encoder.classes_
))

print("\n[7] Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
for i, class_name in enumerate(label_encoder.classes_):
    print(f"  {class_name}: {cm[i]}")

# Feature importance
print("\n[8] Feature Importance:")
feature_names = [
    "Math Score",
    "Verbal Score",
    "Logic Score",
    "Creative Score",
    "Confidence Level",
    "Attendance Rate"
]
importances = rf_model.feature_importances_
for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
    print(f"  {name:20s}: {importance:.4f}")

print("\n[9] Saving model...")
with open('model.pkl', 'wb') as f:
    pickle.dump({
        'model': rf_model,
        'label_encoder': label_encoder,
        'feature_names': feature_names
    }, f)
print(f"✓ Model saved to model.pkl")

print("\n" + "=" * 60)
print("Training Complete!")
print("=" * 60)
