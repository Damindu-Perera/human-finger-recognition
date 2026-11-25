# test_landmark_quality.py

from landmark_quality import LandmarkQualityChecker


checker = LandmarkQualityChecker()


# Create 21 simulated landmarks
test_landmarks = []

for i in range(21):

    test_landmarks.append({
        "id": i,
        "x": 0.3 + (i % 5) * 0.05,
        "y": 0.3 + (i // 5) * 0.05,
        "z": 0.0,
        "pixel_x": 300,
        "pixel_y": 300
    })


# Simulated hand information
test_hand = {
    "label": "Right",
    "confidence": 0.95,
    "landmarks": test_landmarks,
    "bounding_box": {
        "x_min": 300,
        "y_min": 300,
        "x_max": 500,
        "y_max": 500
    }
}


# Evaluate hand
result = checker.evaluate_hand(test_hand)


print("Quality Result:", result)
print("Status:", checker.get_quality_status(result))


# Check expected result
assert result["valid"] is True

print("\nQuality checker test passed!")