
# test_gesture_stabilizer.py

from gesture_stabilizer import GestureStabilizer


stabilizer = GestureStabilizer(
    window_size=7,
    minimum_votes=4
)


print("\nGesture Stabilizer Tests")
print("=" * 50)


# ==========================================
# Test 1: Peace stabilization
# ==========================================

peace_sequence = [
    "Peace",
    "Peace",
    "Unknown",
    "Peace",
    "Peace"
]

print("\nTest 1: Peace stabilization")

for gesture in peace_sequence:

    stable_gesture = stabilizer.update(
        gesture
    )

    print(
        f"Raw: {gesture:<10} | "
        f"Stable: {stable_gesture}"
    )

assert stabilizer.stable_gesture == "Peace"

print("PASS: Peace stabilized successfully")


# ==========================================
# Test 2: Temporary noise
# ==========================================

print("\nTest 2: Temporary noise")

noise_sequence = [
    "Three",
    "Unknown",
    "Pointing"
]

for gesture in noise_sequence:

    stable_gesture = stabilizer.update(
        gesture
    )

    print(
        f"Raw: {gesture:<10} | "
        f"Stable: {stable_gesture}"
    )

print(
    "Current stable gesture:",
    stabilizer.stable_gesture
)


# ==========================================
# Test 3: Transition to Open Palm
# ==========================================

print("\nTest 3: Transition to Open Palm")

open_palm_sequence = [
    "Open Palm",
    "Open Palm",
    "Open Palm",
    "Open Palm"
]

for gesture in open_palm_sequence:

    stable_gesture = stabilizer.update(
        gesture
    )

    print(
        f"Raw: {gesture:<10} | "
        f"Stable: {stable_gesture}"
    )

assert stabilizer.stable_gesture == "Open Palm"

print("PASS: Open Palm stabilized successfully")


# ==========================================
# Test 4: Reset functionality
# ==========================================

print("\nTest 4: Reset")

stabilizer.reset()

assert stabilizer.stable_gesture == "Waiting..."

assert len(stabilizer.history) == 0

print("PASS: Reset works correctly")


print("\n" + "=" * 50)
print("All tests completed successfully!")
