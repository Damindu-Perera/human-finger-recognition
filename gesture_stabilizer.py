
# gesture_stabilizer.py

from collections import deque, Counter


class GestureStabilizer:

    def __init__(
        self,
        window_size=7,
        minimum_votes=4
    ):

        # Store recent gesture predictions
        self.history = deque(
            maxlen=window_size
        )

        # Minimum votes needed for a stable gesture
        self.minimum_votes = minimum_votes

        # Initial stable gesture
        self.stable_gesture = "Waiting..."

    def update(self, raw_gesture):

        """
        Update gesture history and return
        the stabilized gesture.
        """

        # Add the current prediction
        self.history.append(raw_gesture)

        # Count the frequency of each gesture
        gesture_frequency = Counter(
            self.history
        )

        # Find the most frequently predicted gesture
        most_common_gesture, frequency = (
            gesture_frequency.most_common(1)[0]
        )

        # Update stable gesture only if enough votes exist
        if frequency >= self.minimum_votes:

            self.stable_gesture = (
                most_common_gesture
            )

        return self.stable_gesture

    def reset(self):

        # Clear history
        self.history.clear()

        # Reset stable gesture
        self.stable_gesture = "Waiting..."

    def get_history(self):

        # Return recent gesture predictions
        return list(self.history)
