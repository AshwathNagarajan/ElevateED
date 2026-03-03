import csv
import random

# Set random seed for reproducibility
random.seed(42)

# Define career tracks
TRACKS = ["STEM", "Arts", "Business", "Social_Sciences"]

# Generate synthetic data
n_samples = 1000

csv_path = "student_dataset.csv"

# Prepare data
rows = []
track_counts = {track: 0 for track in TRACKS}

for i in range(1, n_samples + 1):
    math_score = random.randint(40, 100)
    verbal_score = random.randint(40, 100)
    logic_score = random.randint(40, 100)
    creative_score = random.randint(30, 95)
    confidence_level = round(random.uniform(0.3, 1.0), 2)
    attendance_rate = round(random.uniform(0.5, 1.0), 2)
    
    # Simple heuristic to assign tracks
    if math_score > 75 and logic_score > 70:
        target_track = "STEM"
    elif creative_score > 75 and verbal_score > 70:
        target_track = "Arts"
    elif verbal_score > 75 and math_score > 65:
        target_track = "Business"
    else:
        target_track = "Social_Sciences"
    
    track_counts[target_track] += 1
    
    rows.append({
        "student_id": i,
        "math_score": math_score,
        "verbal_score": verbal_score,
        "logic_score": logic_score,
        "creative_score": creative_score,
        "confidence_level": confidence_level,
        "attendance_rate": attendance_rate,
        "target_track": target_track
    })

# Write to CSV
with open(csv_path, 'w', newline='') as csvfile:
    fieldnames = [
        "student_id",
        "math_score",
        "verbal_score",
        "logic_score",
        "creative_score",
        "confidence_level",
        "attendance_rate",
        "target_track"
    ]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✓ Dataset generated successfully!")
print(f"✓ Total samples: {n_samples}")
print(f"✓ Saved to: {csv_path}")
print(f"\nTarget Track Distribution:")
for track, count in sorted(track_counts.items()):
    percentage = (count / n_samples) * 100
    print(f"  {track}: {count} ({percentage:.1f}%)")
