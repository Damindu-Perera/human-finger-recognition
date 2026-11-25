# test_hand_tracker.py

from hand_tracker import HandTracker


tracker = HandTracker(
    max_distance=180,
    max_missing_frames=8
)


# ----------------------------------
# Create simulated hand
# ----------------------------------

def create_hand(label, x, y):

    return {
        "label": label,
        "confidence": 0.95,
        "landmarks": [],
        "bounding_box": {
            "x_min": x - 50,
            "y_min": y - 50,
            "x_max": x + 50,
            "y_max": y + 50
        }
    }


# ----------------------------------
# Frame 1: One hand
# ----------------------------------

frame1 = [
    create_hand("Right", 300, 300)
]

tracked_hands = tracker.update(frame1)

first_id = tracked_hands[0]["track_id"]

print("Frame 1:", first_id)

assert first_id == 1


# ----------------------------------
# Frame 2: Same hand moves
# ----------------------------------

frame2 = [
    create_hand("Right", 350, 320)
]

tracked_hands = tracker.update(frame2)

second_id = tracked_hands[0]["track_id"]

print("Frame 2:", second_id)

assert second_id == first_id


# ----------------------------------
# Frame 3: Second hand appears
# ----------------------------------

frame3 = [
    create_hand("Right", 400, 330),
    create_hand("Left", 700, 300)
]

tracked_hands = tracker.update(frame3)

print("Frame 3:")

for hand in tracked_hands:

    print(
        hand["label"],
        "Track ID:",
        hand["track_id"]
    )


# ----------------------------------
# Verify tracking IDs
# ----------------------------------

assert tracked_hands[0]["track_id"] == first_id

assert tracked_hands[1]["track_id"] == 2


# ----------------------------------
# Frame 4: Both hands move
# ----------------------------------

frame4 = [
    create_hand("Right", 450, 350),
    create_hand("Left", 750, 320)
]

tracked_hands = tracker.update(frame4)

print("\nFrame 4:")

for hand in tracked_hands:

    print(
        hand["label"],
        "Track ID:",
        hand["track_id"]
    )


assert tracked_hands[0]["track_id"] == 1
assert tracked_hands[1]["track_id"] == 2


print("\nHand tracker test passed!")