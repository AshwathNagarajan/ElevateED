import csv
import random
from pathlib import Path


RANDOM_SEED = 42
N_SAMPLES = 150_000
OUTPUT_PATH = Path(__file__).with_name("student_dataset.csv")

TRACKS = [
    "Engineering",
    "Computer Science",
    "Data Science",
    "Business Analytics",
    "Design",
    "Humanities",
    "Life Science",
    "Commerce",
]

TRACK_PROFILES = {
    "Engineering": {"math_score": 28, "logic_score": 30, "creative_score": 4, "verbal_score": -3},
    "Computer Science": {"logic_score": 36, "math_score": 18, "creative_score": 8, "verbal_score": -4},
    "Data Science": {"math_score": 34, "logic_score": 22, "verbal_score": 4, "creative_score": -2},
    "Business Analytics": {"math_score": 24, "verbal_score": 18, "logic_score": 14, "creative_score": 2},
    "Design": {"creative_score": 38, "verbal_score": 16, "logic_score": 8, "math_score": -5},
    "Humanities": {"verbal_score": 36, "creative_score": 18, "logic_score": 2, "math_score": -7},
    "Life Science": {"logic_score": 24, "verbal_score": 14, "math_score": 10, "creative_score": 2},
    "Commerce": {"math_score": 26, "verbal_score": 18, "logic_score": 8, "creative_score": -1},
}


def clamp(value, low=0, high=100):
    return max(low, min(high, round(value)))


def bounded_rate(value):
    return round(max(0.0, min(1.0, value)), 2)


def make_student(student_id, target_track):
    """
    Generate one realistic synthetic learner.

    The target track is intentionally influenced by both interest strength and
    learning behavior, then softened with noise so the model learns patterns
    instead of memorizing a perfect rule.
    """
    base = random.gauss(56, 10)
    curiosity = random.gauss(0, 5)
    support_need = random.random()

    math_score = base + random.gauss(0, 8)
    verbal_score = base + random.gauss(0, 8)
    logic_score = base + random.gauss(0, 8)
    creative_score = base + random.gauss(0, 8)

    profile = TRACK_PROFILES[target_track]
    math_score += profile.get("math_score", 0) + curiosity
    verbal_score += profile.get("verbal_score", 0) + (curiosity * 0.45)
    logic_score += profile.get("logic_score", 0) + (curiosity * 0.7)
    creative_score += profile.get("creative_score", 0) + (curiosity * 0.6)

    confidence_level = 0.42 + (max(math_score, verbal_score, logic_score, creative_score) / 220)
    confidence_level -= support_need * 0.18
    attendance_rate = random.gauss(0.84, 0.09) - (support_need * 0.07)

    if target_track in {"Engineering", "Computer Science", "Data Science", "Life Science"}:
        confidence_level += logic_score / 500
    if target_track in {"Humanities", "Design", "Business Analytics", "Commerce"}:
        confidence_level += verbal_score / 520

    quiz_success_rate = (
        max(math_score, verbal_score, logic_score, creative_score) / 100 * 0.58
        + confidence_level * 0.28
        + attendance_rate * 0.14
        + random.gauss(0, 0.045)
    )
    lesson_completion_rate = (
        attendance_rate * 0.42
        + confidence_level * 0.25
        + quiz_success_rate * 0.23
        + random.gauss(0, 0.045)
    )
    learning_pace = (
        lesson_completion_rate * 0.52
        + confidence_level * 0.22
        + (1 - support_need) * 0.16
        + random.gauss(0, 0.04)
    )
    consistency_score = (
        attendance_rate * 0.52
        + lesson_completion_rate * 0.32
        + random.gauss(0, 0.04)
    )

    return {
        "student_id": student_id,
        "math_score": clamp(math_score),
        "verbal_score": clamp(verbal_score),
        "logic_score": clamp(logic_score),
        "creative_score": clamp(creative_score),
        "confidence_level": bounded_rate(confidence_level),
        "attendance_rate": bounded_rate(attendance_rate),
        "quiz_success_rate": bounded_rate(quiz_success_rate),
        "lesson_completion_rate": bounded_rate(lesson_completion_rate),
        "learning_pace": bounded_rate(learning_pace),
        "consistency_score": bounded_rate(consistency_score),
        "target_track": target_track,
    }


def generate_dataset(n_samples=N_SAMPLES):
    random.seed(RANDOM_SEED)
    rows = []
    per_track = n_samples // len(TRACKS)
    student_id = 1

    for track in TRACKS:
        for _ in range(per_track):
            rows.append(make_student(student_id, track))
            student_id += 1

    while len(rows) < n_samples:
        rows.append(make_student(student_id, random.choice(TRACKS)))
        student_id += 1

    random.shuffle(rows)
    return rows


def main():
    rows = generate_dataset()
    fieldnames = [
        "student_id",
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
        "target_track",
    ]

    with OUTPUT_PATH.open("w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Dataset generated successfully")
    print(f"Path: {OUTPUT_PATH}")
    print(f"Rows: {len(rows):,}")
    for track in TRACKS:
        count = sum(1 for row in rows if row["target_track"] == track)
        print(f"{track}: {count:,}")


if __name__ == "__main__":
    main()
