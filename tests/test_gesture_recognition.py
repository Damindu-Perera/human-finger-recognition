
# test_gesture_recognition.py

from gesture_recognition import GestureRecognizer


recognizer = GestureRecognizer()


def create_finger_results(pattern):

    fingers = [
        "Thumb",
        "Index",
        "Middle",
        "Ring",
        "Pinky"
    ]

    results = {}

    for index, finger in enumerate(fingers):

        results[finger] = {
            "extended": pattern[index]
        }

    return results


# Test gestures
test_cases = {
    "Open Palm": [True, True, True, True, True],
    "Fist": [False, False, False, False, False],
    "Peace": [False, True, True, False, False],
    "Three": [False, True, True, True, False],
    "Four": [False, True, True, True, True],
    "Pointing": [False, True, False, False, False],
    "Rock": [False, True, False, False, True],
    "Thumbs Up": [True, False, False, False, False]
}


print("\nGesture Recognition Tests")
print("=" * 40)


for expected_gesture, pattern in test_cases.items():

    finger_results = create_finger_results(
        pattern
    )

    result = recognizer.recognize_gesture(
        finger_results
    )

    recognized_gesture = result["gesture"]

    passed = (
        recognized_gesture == expected_gesture
    )

    status = "PASS" if passed else "FAIL"

    print(
        f"{status} | "
        f"Expected: {expected_gesture:<12} | "
        f"Recognized: {recognized_gesture}"
    )


print("=" * 40)
print("Testing completed.")
