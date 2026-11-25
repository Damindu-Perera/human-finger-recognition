
# gesture_actions.py

import time


class GestureActions:

    def __init__(self, cooldown=1.5):

        # Cooldown prevents an action from triggering
        # repeatedly while a gesture is held.
        self.cooldown = cooldown

        # Store the last trigger time for each gesture.
        self.last_trigger_time = {}

        # Map gestures to their demonstration actions.
        self.action_map = {
            "Thumbs Up": "Confirmation received",
            "Peace": "Special mode activated",
            "Open Palm": "Demo state reset",
            "Pointing": "Selection mode activated",
            "Fist": "Demo stopped",
            "Rock": "Alert triggered",
            "Three": "Mode 3 activated",
            "Four": "Mode 4 activated"
        }

    def execute_action(
        self,
        gesture,
        current_time=None
    ):

        """
        Execute a demonstration action when a
        stabilized gesture is detected.

        A cooldown prevents repeated triggering
        while the gesture is held.
        """

        # Ignore unrecognized or waiting gestures.
        if gesture in ["Unknown", "Waiting...", None]:
            return None

        # Use current time if it is not provided.
        if current_time is None:
            current_time = time.time()

        # Check if this gesture has an action.
        if gesture not in self.action_map:
            return None

        # Get previous trigger time.
        last_trigger = self.last_trigger_time.get(
            gesture,
            0
        )

        # Check cooldown.
        if (
            current_time - last_trigger
            < self.cooldown
        ):
            return None

        # Update last trigger time.
        self.last_trigger_time[gesture] = (
            current_time
        )

        # Get action description.
        action_message = self.action_map[gesture]

        # Print demonstration action.
        print(
            f"[ACTION] {gesture}: "
            f"{action_message}"
        )

        return {
            "gesture": gesture,
            "action": action_message,
            "triggered": True
        }

    def reset(self):

        # Clear action cooldown history.
        self.last_trigger_time.clear()
