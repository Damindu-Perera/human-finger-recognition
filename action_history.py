from collections import deque
from datetime import datetime


class ActionHistory:
    def __init__(self, max_history=50):
        """
        Stores recent gesture-triggered actions.

        Args:
            max_history (int): Maximum number of actions to keep.
        """
        if max_history <= 0:
            raise ValueError("max_history must be greater than 0")

        self.max_history = max_history
        self.history = deque(maxlen=max_history)

    def add_action(self, track_id, gesture, action):
        """
        Record a triggered gesture action.

        Args:
            track_id: Hand tracking ID.
            gesture: Recognized gesture name.
            action: Action message.

        Returns:
            dict: Recorded action entry.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")

        entry = {
            "track_id": track_id,
            "gesture": gesture,
            "action": action,
            "timestamp": timestamp
        }

        self.history.append(entry)

        return entry

    def get_history(self):
        """Return all stored actions, oldest to newest."""
        return list(self.history)

    def get_recent_actions(self, limit=5):
        """Return the most recent actions."""
        if limit <= 0:
            return []

        return list(self.history)[-limit:]

    def get_latest_action(self):
        """Return the most recent action or None."""
        if not self.history:
            return None

        return self.history[-1]

    def clear_history(self):
        """Remove all stored actions."""
        self.history.clear()

    def get_history_size(self):
        """Return the current number of stored actions."""
        return len(self.history)