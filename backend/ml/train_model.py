import csv
import json
import pickle
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from sklearn.ensemble import ExtraTreesClassifier, HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder


DATASET_PATH = Path(__file__).with_name("student_dataset.csv")
MODEL_PATH = Path(__file__).with_name("model.pkl")
METRICS_PATH = Path(__file__).with_name("model_metrics.json")

FEATURE_NAMES = [
    "math_score",
    "verbal_score",
    "logic_score",
    "creative_score",
    "confidence_level",
    "attendance_rate",
    "quiz_success_rate",
    "lesson_completion_rate",
    "learning_pace",
    "consistency_score",
]


def load_dataset(filepath):
    x_rows = []
    y_rows = []
    with filepath.open("r", newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            x_rows.append([
                float(row["math_score"]) / 100.0,
                float(row["verbal_score"]) / 100.0,
                float(row["logic_score"]) / 100.0,
                float(row["creative_score"]) / 100.0,
                float(row["confidence_level"]),
                float(row["attendance_rate"]),
                float(row["quiz_success_rate"]),
                float(row["lesson_completion_rate"]),
                float(row["learning_pace"]),
                float(row["consistency_score"]),
            ])
            y_rows.append(row["target_track"])
    return np.array(x_rows, dtype=np.float32), y_rows


def build_candidates():
    return {
        "hist_gradient_boosting": HistGradientBoostingClassifier(
            learning_rate=0.08,
            max_iter=240,
            max_leaf_nodes=31,
            l2_regularization=0.02,
            random_state=42,
        ),
        "extra_trees": ExtraTreesClassifier(
            n_estimators=220,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=220,
            max_depth=18,
            min_samples_leaf=2,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1,
        ),
    }


def main():
    print("=" * 72)
    print("ElevateED ML Training: Student Guidance Track Model")
    print("=" * 72)

    x, y = load_dataset(DATASET_PATH)
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y_encoded,
        test_size=0.2,
        random_state=42,
        stratify=y_encoded,
    )

    print(f"Rows: {len(x):,}")
    print(f"Features: {len(FEATURE_NAMES)}")
    print(f"Classes: {list(encoder.classes_)}")
    print()

    results = {}
    best_name = None
    best_model = None
    best_score = -1

    for name, model in build_candidates().items():
        print(f"Training {name}...")
        model.fit(x_train, y_train)
        predictions = model.predict(x_test)
        accuracy = accuracy_score(y_test, predictions)
        macro_f1 = f1_score(y_test, predictions, average="macro")
        weighted_f1 = f1_score(y_test, predictions, average="weighted")
        selection_score = (macro_f1 * 0.7) + (accuracy * 0.3)

        results[name] = {
            "accuracy": round(float(accuracy), 5),
            "macro_f1": round(float(macro_f1), 5),
            "weighted_f1": round(float(weighted_f1), 5),
            "selection_score": round(float(selection_score), 5),
        }

        print(
            f"  accuracy={accuracy:.4f} macro_f1={macro_f1:.4f} "
            f"weighted_f1={weighted_f1:.4f}"
        )

        if selection_score > best_score:
            best_score = selection_score
            best_name = name
            best_model = model

    best_predictions = best_model.predict(x_test)
    report = classification_report(
        y_test,
        best_predictions,
        target_names=encoder.classes_,
        output_dict=True,
    )

    model_bundle = {
        "model": best_model,
        "label_encoder": encoder,
        "feature_names": FEATURE_NAMES,
        "model_name": best_name,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "dataset_rows": len(x),
        "metrics": results[best_name],
    }
    with MODEL_PATH.open("wb") as model_file:
        pickle.dump(model_bundle, model_file)

    metrics = {
        "selected_model": best_name,
        "dataset_rows": len(x),
        "feature_names": FEATURE_NAMES,
        "classes": list(encoder.classes_),
        "candidate_results": results,
        "classification_report": report,
        "created_at": model_bundle["created_at"],
    }
    METRICS_PATH.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print()
    print(f"Selected model: {best_name}")
    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved metrics: {METRICS_PATH}")
    print("=" * 72)


if __name__ == "__main__":
    main()
