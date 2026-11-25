# count_stabilizer.py

from collections import deque, Counter


class CountStabilizer:

    def __init__(
        self,
        window_size=7,
        minimum_votes=4
    ):

        # Store recent finger counts
        self.history = deque(
            maxlen=window_size
        )

        # Minimum votes required to update count
        self.minimum_votes = minimum_votes

        # Current stable count
        self.stable_count = 0

    # ----------------------------------
    # Update count with new prediction
    # ----------------------------------

    def update(self, raw_count):

        # Add latest count to history
        self.history.append(raw_count)

        # Count frequency of each prediction
        count_frequency = Counter(
            self.history
        )

        # Find the most common count
        most_common_count, frequency = (
            count_frequency.most_common(1)[0]
        )

        # Update only if enough votes exist
        if frequency >= self.minimum_votes:

            self.stable_count = (
                most_common_count
            )

        # Otherwise retain previous stable count
        return self.stable_count

    # ----------------------------------
    # Reset stabilizer
    # ----------------------------------

    def reset(self):

        self.history.clear()

        self.stable_count = 0

    # ----------------------------------
    # Get current history
    # ----------------------------------

    def get_history(self):

        return list(self.history)